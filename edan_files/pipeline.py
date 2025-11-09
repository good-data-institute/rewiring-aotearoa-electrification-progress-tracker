"""
===============================================================================
Script:      transport.py
Purpose:     Implements a Medallion Architecture pipeline (Bronze → Silver → Gold)
             for motor vehicle data from Waka Kotahi open fleet datasets.

Author:      Edan Fisher
Date:        19 October 2025

Data Source:
    Waka Kotahi NZ Transport Agency Open Data Portal
    https://opendata-nzta.opendata.arcgis.com/datasets/NZTA::motor-vehicle-register/about

Description:
    Downloads and processes the motor vehicle register from the CSV file.
    The pipeline:
        • Bronze Layer: Downloads the complete MVR dataset from the open data portal - purpose is to store a raw, immutable snapshot
        • Silver Layer: Fix data types, remove unecessary columns, fix geometry types - purpose is to store clean data
        • Gold Layer: Implement all aggregates needed to supply the metrics outlined by Rewiring Aotearoa + GDI

Outputs:
    • data/bronze/mvr_bronze_stream.parquet
    • data/silver/mvr_silver_cleaned.parquet
    • data/gold/*
    
===============================================================================
"""

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests
from io import StringIO
import duckdb
import os
from pathlib import Path

def bronze_ingest():
    CSV_URL = "https://hub.arcgis.com/api/v3/datasets/95182f7804bf4eeeac31b2747e841a70_0/downloads/data?format=csv&spatialRefId=2193&where=1%3D1"
    BRONZE_PATH = "data/bronze/mvr_bronze_stream.parquet"
    CHUNK_SIZE = 500_000  # adjust to balance speed vs memory
    os.makedirs("data/bronze", exist_ok=True)

    # Step 1: Stream CSV from URL
    response = requests.get(CSV_URL, stream=True)
    response.raise_for_status()

    # Step 2: Prepare Parquet writer
    first_chunk = True
    parquet_writer = None

    for chunk in pd.read_csv(StringIO(response.content.decode('utf-8')), chunksize=CHUNK_SIZE, dtype=str):
        # Convert to PyArrow Table
        table = pa.Table.from_pandas(chunk, preserve_index=False)
        
        # Initialize or append to Parquet
        if first_chunk:
            parquet_writer = pq.ParquetWriter(BRONZE_PATH, table.schema, compression='snappy')
            first_chunk = False
        
        parquet_writer.write_table(table)
        print(f"✅ Processed chunk with {len(chunk):,} rows")

    # Close writer
    if parquet_writer:
        parquet_writer.close()

    print(f"✅ Bronze layer saved to {BRONZE_PATH}")

def silver_transform():
    BRONZE_PATH = "data/bronze/mvr_bronze_stream.parquet"
    SILVER_PATH = "data/silver/mvr_silver_cleaned.parquet"
    os.makedirs("data/silver", exist_ok=True)

    # Connect to DuckDB
    con = duckdb.connect(database=':memory:')

    # Read bronze parquet into DuckDB
    con.execute(f"""
        CREATE TABLE bronze AS
        SELECT * FROM read_parquet('{BRONZE_PATH}')
    """)

    # Transform and clean for silver layer
    con.execute("""
        CREATE TABLE silver AS
        SELECT
            OBJECTID,
            FIRST_NZ_REGISTRATION_YEAR AS 'Year',
            FIRST_NZ_REGISTRATION_MONTH AS 'Month',
            TLA AS 'Region',
            IMPORT_STATUS AS 'Condition',
                
            -- Map INDUSTRY_CLASS to simplified PRIVATE / COMMERCIAL / PUBLIC
                
            CASE
                WHEN INDUSTRY_CLASS = 'PRIVATE' THEN 'Private'
                WHEN INDUSTRY_CLASS IN ('BUSINESS/FINANCIAL', 'COMMERCIAL ROAD TRANSPORT', 'CONSTRUCTING',
                                        'WHOLESALE/RETAIL/TRADE', 'TOURISM/LEISURE', 'AGRICULTURE/FORESTRY/FISHING',
                                        'COMMUNITY SERVICES', 'ELECTRICITY/GAS/WATER', 'VEHICLE TRADER', 'MANUFACTURING',
                                        'MINING/QUARRYING', 'TRANSPORT NON ROAD', 'VEHICLE DEALER') THEN 'Commercial'
                ELSE 'Other'
            END AS Category,

            -- Ensure numeric comparisons work by casting GROSS_VEHICLE_MASS
                
            CASE
                WHEN VEHICLE_TYPE = 'PASSENGER CAR/VAN' THEN 'Light Passenger Vehicle'
                WHEN VEHICLE_TYPE = 'BUS' THEN 'Bus'
                WHEN VEHICLE_TYPE IN ('MOTOR CARAVAN', 'GOODS VAN/TRUCK/UTILITY') 
                    AND CAST(GROSS_VEHICLE_MASS AS DOUBLE) <= 3500 THEN 'Light Commercial Vehicle'
                WHEN VEHICLE_TYPE IN ('MOTOR CARAVAN', 'GOODS VAN/TRUCK/UTILITY') 
                    AND CAST(GROSS_VEHICLE_MASS AS DOUBLE) > 3500 THEN 'Heavy Vehicle'
                WHEN VEHICLE_TYPE = 'ATV' THEN 'ATV'
                WHEN VEHICLE_TYPE IN ('MOTORCYCLE', 'MOPED') THEN 'Motorcycle'
                ELSE 'Other'
            END AS Sub_Category,
                
            -- Map motive power to familiar terms agreed upon in our spreadsheet 
                   
            CASE
                WHEN MOTIVE_POWER = 'PETROL' THEN 'Petrol'
                WHEN MOTIVE_POWER = 'DIESEL' THEN 'Diesel'
                WHEN MOTIVE_POWER IN ('PETROL HYBRID', 'DIESEL HYBRID') THEN 'HEV'
                WHEN MOTIVE_POWER IN ('PETROL ELECTRIC HYBRID', 'PLUGIN PETROL HYBRID') THEN 'PHEV'
                WHEN MOTIVE_POWER IN ('ELECTRIC', 'ELECTRIC [PETROL EXTENDED]', 'ELECTRIC [DIESEL EXTENDED]') THEN 'BEV'
                WHEN MOTIVE_POWER IN ('ELECTRIC FUEL CELL HYDROGEN', 'ELECTRIC FUEL CELL OTHER', 
                                    'PLUG IN FUEL CELL HYDROGEN HYBRID', 'PLUG IN FUEL CELL OTHER HYBRID') THEN 'FCEV'
                WHEN MOTIVE_POWER IN ('LPG', 'CNG') THEN 'Petrol'
                ELSE 'Other'
            END AS Fuel_Type
                
        FROM bronze
    """)

    # Write silver layer to Parquet
    con.execute(f"""
        COPY silver TO '{SILVER_PATH}' (FORMAT PARQUET, COMPRESSION 'snappy')
    """)
    con.close()
    print(f"✅ Silver layer saved to {SILVER_PATH}")

def gold_aggregate(df, metrics_config):
    Path("data/gold").mkdir(parents=True, exist_ok=True)

    for metric in metrics_config:
        metric_id = metric["metric_id"]
        filters = metric.get("filter_conditions", {})
        metric_group = metric["metric_group"]
        category = metric["Category"]
        sub_category = metric["Sub_Category"]
        fuel_type = metric.get("Fuel_Type")
        output_name = metric["output_name"]
        calculation = metric.get("calculation", "count")  # default is count

        # Apply filters
        df_filtered = df.copy()
        for col, val in filters.items():
            df_filtered = df_filtered[df_filtered[col] == val]

        # Determine aggregation (grouping by year, month, and region)
        group_cols = ["Year", "Month", "Region"]
        agg_col_name = metric_id

        # The calculation field will detect if this is a fleet percentage metric
        if calculation == "percentage_electrified":
            # Total fleet
            total_fleet = df_filtered.groupby(group_cols)["OBJECTID"].count().rename("total_fleet")

            # EV fleet (assuming what RA consider 'the EV fleet' is BEV vehicles only)
            ev_fleet = df_filtered[df_filtered["Fuel_Type"] == "BEV"].groupby(group_cols)["OBJECTID"].count().rename("ev_fleet")

            # Merge and calculate %
            grouped = pd.merge(total_fleet, ev_fleet, left_index=True, right_index=True, how="left").fillna(0)
            grouped[agg_col_name] = grouped["ev_fleet"] / grouped["total_fleet"] * 100
            grouped = grouped.reset_index()
        else:
            grouped = df_filtered.groupby(group_cols)["OBJECTID"].count().reset_index()
            grouped = grouped.rename(columns={"OBJECTID": agg_col_name})

        # Add metadata
        grouped["Metric Group"] = metric_group
        grouped["Category"] = category
        grouped["Sub-Category"] = sub_category
        grouped["Fuel Type"] = fuel_type

        # Reorder columns
        final_cols = ["Year", "Month", "Region", "Metric Group", "Category", "Sub-Category", "Fuel Type", agg_col_name]
        grouped = grouped[final_cols]

        # Save Parquet
        file_path = f"data/gold/{output_name}.parquet"
        grouped.to_parquet(file_path, index=False)
        print(f"✅ Saved {output_name} ({len(grouped):,} rows)")

    return True

# Test gold function for NZ wide metrics - will need to check with Jenny if this is what she wants, or just region-based only
def gold_aggregate_nz(df, metrics_config):
    Path("data/gold_nz").mkdir(parents=True, exist_ok=True)

    for metric in metrics_config:
        metric_id = metric["metric_id"]
        filters = metric.get("filter_conditions", {})
        metric_group = metric["metric_group"]
        category = metric["Category"]
        sub_category = metric["Sub_Category"]
        fuel_type = metric.get("Fuel_Type")
        output_name = metric["output_name"]
        calculation = metric.get("calculation", "count")  # default is count

        # Apply filters
        df_filtered = df.copy()
        for col, val in filters.items():
            if isinstance(val, list):
                df_filtered = df_filtered[df_filtered[col].isin(val)]
            else:
                df_filtered = df_filtered[df_filtered[col] == val]

        # --- NATIONAL LEVEL AGGREGATION ---
        group_cols = ["Year", "Month"]  # No Region
        agg_col_name = metric_id

        if calculation == "percentage_electrified":
            # Total fleet
            total_fleet = df_filtered.groupby(group_cols)["OBJECTID"].count().rename("total_fleet")

            # EV fleet (assuming BEV only)
            ev_fleet = df_filtered[df_filtered["Fuel_Type"] == "BEV"].groupby(group_cols)["OBJECTID"].count().rename("ev_fleet")

            # Merge and calculate % electrified
            grouped = pd.merge(total_fleet, ev_fleet, left_index=True, right_index=True, how="left").fillna(0)
            grouped[agg_col_name] = grouped["ev_fleet"] / grouped["total_fleet"] * 100
            grouped = grouped.reset_index()
        else:
            grouped = (
                df_filtered.groupby(group_cols)["OBJECTID"]
                .count()
                .reset_index()
                .rename(columns={"OBJECTID": agg_col_name})
            )

        # Add metadata
        grouped["Metric Group"] = metric_group
        grouped["Category"] = category
        grouped["Sub-Category"] = sub_category
        grouped["Fuel Type"] = fuel_type
        grouped["Region"] = "New Zealand"  # Optional — keep a single constant for clarity

        # Reorder columns
        final_cols = [
            "Year", "Month", "Region", "Metric Group",
            "Category", "Sub-Category", "Fuel Type", agg_col_name
        ]
        grouped = grouped[final_cols]

        # Save Parquet
        file_path = f"data/gold_nz/{output_name}_nz.parquet"
        grouped.to_parquet(file_path, index=False)
        print(f"✅ Saved {output_name}_nz ({len(grouped):,} rows)")

    return True
