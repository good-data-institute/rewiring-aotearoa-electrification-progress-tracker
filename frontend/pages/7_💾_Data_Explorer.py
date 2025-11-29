"""Data Explorer - Raw Data Access and Export.

This page provides data table viewing and CSV export functionality.
"""

import os
import sys

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard_utils import (
    create_paginated_dataframe,
    fetch_dataset,
    filter_annual_aggregates,
)

load_dotenv()

BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
API_BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

st.set_page_config(page_title="Data Explorer", page_icon="💾", layout="wide")

st.title("💾 Data Explorer")
st.markdown("**Browse, filter, and export raw datasets**")

# Sidebar
st.sidebar.header("🔍 Data Selection")

dataset_map = {
    "EECA - Electricity Percentage": "eeca_electricity_percentage",
    "EECA - Energy by Fuel": "eeca_energy_by_fuel",
    "EECA - Boiler Energy": "eeca_boiler_energy",
    "GIC - Gas Connections": "gic_analytics",
    "EMI - Renewable Generation": "emi_generation_analytics",
    "EMI - Battery Penetration (Commercial)": "battery_penetration_commercial",
    "EMI - Battery Penetration (Residential)": "battery_penetration_residential",
    "EMI - Solar Capacity": "solar_penetration",
    "EMI - Battery Capacity": "battery_capacity",
    "Waka Kotahi - EV Count": "waka_kotahi_ev",
    "Waka Kotahi - Fossil Fuel Vehicles": "waka_kotahi_ff",
    "Waka Kotahi - New EV Sales": "waka_kotahi_new_ev",
    "Waka Kotahi - Used EV Imports": "waka_kotahi_used_ev",
    "Waka Kotahi - Fleet Electrification": "waka_kotahi_fleet_elec",
}

selected_dataset_name = st.sidebar.selectbox(
    "Select Dataset",
    options=list(dataset_map.keys()),
)

dataset_key = dataset_map[selected_dataset_name]

year_range = st.sidebar.slider("Year Range", 2010, 2025, (2015, 2025))

include_annual = st.sidebar.checkbox("Include Annual Aggregates", False)

load_full = st.sidebar.checkbox(
    "Load Full Dataset",
    value=False,
    help="Warning: Some datasets have 100k+ rows. May be slow.",
)

# Fetch data
with st.spinner(f"Loading {selected_dataset_name}..."):
    try:
        limit = None if load_full else 10000
        df = fetch_dataset(
            API_BASE_URL,
            dataset_key,
            year_min=year_range[0],
            year_max=year_range[1],
            limit=limit,
        )
        df = filter_annual_aggregates(df, include_annual)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        df = pd.DataFrame()

if not df.empty:
    st.success(f"✓ Loaded {len(df):,} rows")

    # Dataset Info
    st.subheader("Dataset Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        if "Year" in df.columns:
            years = df["Year"].unique()
            st.metric("Year Range", f"{min(years)}-{max(years)}")

    # Column Info
    with st.expander("Column Details"):
        col_info = pd.DataFrame(
            {
                "Column": df.columns,
                "Type": df.dtypes.astype(str),
                "Non-Null Count": df.count(),
                "Null Count": df.isnull().sum(),
            }
        )
        st.dataframe(col_info, use_container_width=True)

    # Summary Statistics
    with st.expander("Summary Statistics"):
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            st.dataframe(df[numeric_cols].describe(), use_container_width=True)
        else:
            st.info("No numeric columns in dataset")

    st.markdown("---")

    # Data Preview
    st.subheader("Data Preview")

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        if "Region" in df.columns:
            regions = st.multiselect(
                "Filter by Region",
                options=sorted(df["Region"].unique()),
            )
            if regions:
                df = df[df["Region"].isin(regions)]

    with col2:
        if "Category" in df.columns:
            categories = st.multiselect(
                "Filter by Category",
                options=sorted(df["Category"].unique()),
            )
            if categories:
                df = df[df["Category"].isin(categories)]

    # Search
    search_term = st.text_input("Search (case-insensitive)", "")
    if search_term:
        mask = (
            df.astype(str)
            .apply(lambda x: x.str.contains(search_term, case=False, na=False))
            .any(axis=1)
        )
        df = df[mask]
        st.info(f"Found {len(df):,} matching rows")

    # Paginated Table
    st.write(f"Showing data ({len(df):,} rows after filters)")
    df_paginated = create_paginated_dataframe(
        df, page_size=100, page_key=f"data_explorer_{dataset_key}"
    )
    st.dataframe(df_paginated, use_container_width=True)

    # Download
    st.markdown("---")
    st.subheader("Export Data")

    col1, col2 = st.columns(2)

    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f"{dataset_key}_{year_range[0]}_{year_range[1]}.csv",
            mime="text/csv",
        )

    with col2:
        st.download_button(
            label="📥 Download Displayed Page as CSV",
            data=df_paginated.to_csv(index=False),
            file_name=f"{dataset_key}_page.csv",
            mime="text/csv",
        )

else:
    st.warning("No data available for selected filters")

st.markdown("---")

# Data Dictionary
st.subheader("Data Dictionary")

st.markdown("""
### Dataset Descriptions

**EECA (Energy Efficiency and Conservation Authority)**
- **Electricity Percentage**: Electricity's share of total energy consumption
- **Energy by Fuel**: Energy consumption breakdown by fuel type (Coal, Diesel, Petrol, Electricity, etc.)
- **Boiler Energy**: Fossil fuel energy consumption in boilers

**GIC (Gas Industry Company)**
- **Gas Connections**: New gas connection installations

**EMI (Electricity Market Information)**
- **Renewable Generation**: Percentage of renewable energy in electricity generation
- **Battery Penetration**: Percentage of connections/installations with batteries
- **Solar Capacity**: Megawatts of solar capacity installed
- **Battery Capacity**: Megawatts of battery capacity installed

**Waka Kotahi (Transport)**
- **EV Count**: Total Battery Electric Vehicles registered
- **Fossil Fuel Vehicles**: Count of petrol/diesel vehicles
- **New EV Sales**: New (not used) EV purchases
- **Used EV Imports**: Used (imported) EV purchases
- **Fleet Electrification**: Percentage of vehicle fleet that is electric
""")

st.caption(
    "💾 Use filters and search to explore specific data points, then export for further analysis"
)
