"""Data Explorer - Raw Data Access and Export.

This page provides data table viewing and CSV export functionality.
"""

import os
import sys

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard_utils import (
    create_paginated_dataframe,
    fetch_dataset,
    filter_annual_aggregates,
)

# Add global refresh button to sidebar
from dashboard_utils import add_global_refresh_button, add_page_refresh_button

load_dotenv()

BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
API_BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

st.set_page_config(page_title="Data Explorer", page_icon="💾", layout="wide")

st.title("💾 Data Explorer")
st.markdown("**Browse, filter, and export raw datasets with metadata**")

add_global_refresh_button(API_BASE_URL)

# Add tabs for different views
tab1, tab2 = st.tabs(["📊 Explore Data", "📋 All Metrics"])


# Fetch metadata
@st.cache_data(ttl=300)
def fetch_metadata():
    """Fetch metadata for all metrics from the API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/metrics/metadata/by-sector", timeout=60
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch metadata: {e}")
        return None


# Fetch metadata
metadata_response = fetch_metadata()

if not metadata_response:
    st.error("Unable to load metrics metadata. Please check backend connection.")
    st.stop()

sectors_data = metadata_response.get("sectors", {})

# Tab 2: Show all metrics as a browsable list
with tab2:
    st.header("📋 All Available Metrics")
    st.markdown(
        "Complete list of all metrics in the system, grouped by sector with metadata."
    )

    for sector, metrics in sectors_data.items():
        with st.expander(f"**{sector}** ({len(metrics)} metrics)", expanded=False):
            for metric in metrics:
                st.markdown(f"### {metric['friendly_name']}")
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**Description:** {metric['description']}")
                    st.markdown(f"**Source:** {metric['source_api']}")
                    st.markdown(f"**Dimensions:** {', '.join(metric['dimensions'])}")
                with col2:
                    st.markdown(f"**Metric ID:** `{metric['metric_id']}`")
                    st.markdown(f"**Dataset Key:** `{metric['dataset_key']}`")
                    st.markdown(f"**Unit:** {metric['unit']}")

                # Show categories if available
                if metric.get("categories"):
                    st.markdown(
                        f"**Categories:** {', '.join(metric['categories'][:10])}{'...' if len(metric['categories']) > 10 else ''}"
                    )

                st.markdown("---")

# Tab 1: Data Explorer
with tab1:
    # Sidebar
    st.sidebar.header("🔍 Data Selection")

    # Group metrics by sector
    sector_options = list(sectors_data.keys())
    selected_sector = st.sidebar.selectbox(
        "Select Sector",
        options=sector_options,
        help="Choose a sector to view available metrics",
    )

    # Get metrics for selected sector
    sector_metrics = sectors_data.get(selected_sector, [])

    # Create dataset options for the selected sector
    dataset_options = {m["friendly_name"]: m["dataset_key"] for m in sector_metrics}

    selected_dataset_name = st.sidebar.selectbox(
        "Select Metric",
        options=list(dataset_options.keys()),
        help="Choose a specific metric to explore",
    )

    dataset_key = dataset_options[selected_dataset_name]

    # Get metadata for selected dataset
    selected_metadata = next(
        (m for m in sector_metrics if m["dataset_key"] == dataset_key), None
    )

    # Display Metadata Panel
    if selected_metadata:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📋 Metric Information")
        st.sidebar.markdown(f"**Metric ID:** `{selected_metadata['metric_id']}`")
        st.sidebar.markdown(f"**Description:** {selected_metadata['description']}")
        st.sidebar.markdown(f"**Source:** {selected_metadata['source_api']}")
        st.sidebar.markdown(f"**Unit:** {selected_metadata['unit']}")
        st.sidebar.markdown(
            f"**Dimensions:** {', '.join(selected_metadata['dimensions'])}"
        )

    st.sidebar.markdown("---")

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
        # Add page refresh button at top
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"✓ Loaded {len(df):,} rows")
        with col2:
            add_page_refresh_button(datasets=[dataset_key])

        # Metric Metadata Display
        if selected_metadata:
            with st.expander("📊 Metric Details", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Metric ID:** `{selected_metadata['metric_id']}`")
                    st.markdown(f"**Sector:** {selected_metadata['sector']}")
                    st.markdown(f"**Unit:** {selected_metadata['unit']}")
                with col2:
                    st.markdown(f"**Source API:** {selected_metadata['source_api']}")
                    st.markdown(
                        f"**Pipeline:** `{selected_metadata['pipeline_file'].split('/')[-1]}`"
                    )
                with col3:
                    st.markdown(
                        f"**Dimensions:** {', '.join(selected_metadata['dimensions'])}"
                    )
                    if selected_metadata.get("categories"):
                        st.markdown(
                            f"**Categories:** {', '.join(selected_metadata['categories'][:5])}{'...' if len(selected_metadata['categories']) > 5 else ''}"
                        )

                st.markdown(f"**Description:** {selected_metadata['description']}")

                # Upstream dependencies
                if selected_metadata.get("upstream_dependencies"):
                    st.markdown("**Upstream Dependencies:**")
                    for dep in selected_metadata["upstream_dependencies"]:
                        st.markdown(f"  - `{dep}`")

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
            st.dataframe(col_info, width="stretch")

        # Summary Statistics
        with st.expander("Summary Statistics"):
            numeric_cols = df.select_dtypes(include=["number"]).columns
            if len(numeric_cols) > 0:
                st.dataframe(df[numeric_cols].describe(), width="stretch")
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
        st.dataframe(df_paginated, width="stretch")

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

    st.markdown(
        """
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
"""
    )

    st.caption(
        "💾 Use filters and search to explore specific data points, then export for further analysis"
    )
