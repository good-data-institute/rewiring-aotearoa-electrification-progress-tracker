"""Transform: Waka Kotahi Motor Vehicle Register data pipeline.

This script handles data transformation:
1. Reads raw Parquet files from raw storage
2. Cleans and transforms the data with business logic
3. Saves processed data as single consolidated Parquet file
"""

from pathlib import Path

import duckdb

from etl.core.config import get_settings
from etl.core.pipeline import ProcessedLayer


class WakaKotahiMVRTransformer(ProcessedLayer):
    """Data transformer for Waka Kotahi MVR: Transform raw data to processed."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Transform raw Parquet to processed format.

        Applies data cleaning and business logic transformations:
        - Fixes data types
        - Maps industry classes to simplified categories
        - Classifies vehicle types into sub-categories
        - Maps motive power to standardized fuel types

        Args:
            input_path: Path to raw Parquet file
            output_path: Path to save processed Parquet file
        """
        print(f"\n{'='*80}")
        print("WAKA KOTAHI MOTOR VEHICLE REGISTER: Transform Raw to Processed")
        print(f"{'='*80}")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print("\n[1/3] Loading raw data from Parquet...")
        print(f"      Input: {input_path}")

        # Step 1: Connect to DuckDB and load raw data
        con = duckdb.connect(database=":memory:")

        # Read raw parquet into DuckDB
        con.execute(f"""
            CREATE TABLE raw AS
            SELECT * FROM read_parquet('{input_path}')
        """)

        row_count = con.execute("SELECT COUNT(*) FROM raw").fetchone()[0]
        print(f"      ✓ Loaded {row_count:,} rows")

        # Step 2: Apply transformations using SQL
        print("\n[2/3] Applying transformations:")
        print("      - Mapping industry classes to categories...")
        print("      - Classifying vehicle types and sub-categories...")
        print("      - Standardizing fuel types...")

        con.execute("""
            CREATE TABLE processed AS
            SELECT
                OBJECTID,
                FIRST_NZ_REGISTRATION_YEAR AS Year,
                FIRST_NZ_REGISTRATION_MONTH AS Month,
                TLA AS Region,
                IMPORT_STATUS AS Condition,

                -- Map INDUSTRY_CLASS to simplified PRIVATE / COMMERCIAL / PUBLIC
                CASE
                    WHEN INDUSTRY_CLASS = 'PRIVATE' THEN 'Private'
                    WHEN INDUSTRY_CLASS IN (
                        'BUSINESS/FINANCIAL', 'COMMERCIAL ROAD TRANSPORT', 'CONSTRUCTING',
                        'WHOLESALE/RETAIL/TRADE', 'TOURISM/LEISURE', 'AGRICULTURE/FORESTRY/FISHING',
                        'COMMUNITY SERVICES', 'ELECTRICITY/GAS/WATER', 'VEHICLE TRADER', 'MANUFACTURING',
                        'MINING/QUARRYING', 'TRANSPORT NON ROAD', 'VEHICLE DEALER'
                    ) THEN 'Commercial'
                    ELSE 'Other'
                END AS Category,

                -- Classify vehicle types with mass-based logic for LCV/HV
                CASE
                    WHEN VEHICLE_TYPE = 'PASSENGER CAR/VAN' THEN 'Light Passenger Vehicle'
                    WHEN VEHICLE_TYPE = 'BUS' THEN 'Bus'
                    WHEN VEHICLE_TYPE IN ('MOTOR CARAVAN', 'GOODS VAN/TRUCK/UTILITY')
                        AND TRY_CAST(GROSS_VEHICLE_MASS AS DOUBLE) <= 3500 THEN 'Light Commercial Vehicle'
                    WHEN VEHICLE_TYPE IN ('MOTOR CARAVAN', 'GOODS VAN/TRUCK/UTILITY')
                        AND TRY_CAST(GROSS_VEHICLE_MASS AS DOUBLE) > 3500 THEN 'Heavy Vehicle'
                    WHEN VEHICLE_TYPE = 'ATV' THEN 'ATV'
                    WHEN VEHICLE_TYPE IN ('MOTORCYCLE', 'MOPED') THEN 'Motorcycle'
                    ELSE 'Other'
                END AS Sub_Category,

                -- Map motive power to standardized fuel types
                CASE
                    WHEN MOTIVE_POWER = 'PETROL' THEN 'Petrol'
                    WHEN MOTIVE_POWER = 'DIESEL' THEN 'Diesel'
                    WHEN MOTIVE_POWER IN ('PETROL HYBRID', 'DIESEL HYBRID') THEN 'HEV'
                    WHEN MOTIVE_POWER IN ('PETROL ELECTRIC HYBRID', 'PLUGIN PETROL HYBRID') THEN 'PHEV'
                    WHEN MOTIVE_POWER IN ('ELECTRIC', 'ELECTRIC [PETROL EXTENDED]', 'ELECTRIC [DIESEL EXTENDED]') THEN 'BEV'
                    WHEN MOTIVE_POWER IN (
                        'ELECTRIC FUEL CELL HYDROGEN', 'ELECTRIC FUEL CELL OTHER',
                        'PLUG IN FUEL CELL HYDROGEN HYBRID', 'PLUG IN FUEL CELL OTHER HYBRID'
                    ) THEN 'FCEV'
                    WHEN MOTIVE_POWER IN ('LPG', 'CNG') THEN 'Petrol'
                    ELSE 'Other'
                END AS Fuel_Type

            FROM raw
        """)

        processed_count = con.execute("SELECT COUNT(*) FROM processed").fetchone()[0]
        print(f"      ✓ Transformed {processed_count:,} rows")

        # Step 3: Write to Parquet
        print("\n[3/3] Writing processed data to Parquet...")
        print(f"      Output: {output_path}")

        con.execute(f"""
            COPY processed TO '{output_path}' (FORMAT PARQUET, COMPRESSION 'snappy')
        """)

        con.close()

        print(f"\n{'='*80}")
        print(f"✓ Transformation complete: {output_path}")
        print(f"  Rows processed: {processed_count:,}")
        print(f"{'='*80}\n")


def main():
    """Main function to run the transformation pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = settings.raw_dir / "waka_kotahi_mvr" / "mvr_raw.parquet"
    output_path = settings.processed_dir / "waka_kotahi_mvr" / "mvr_processed.parquet"

    # Create transformer
    transformer = WakaKotahiMVRTransformer()

    # Run the transformation process
    try:
        transformer.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Transformation failed: {e}")
        raise


if __name__ == "__main__":
    main()
