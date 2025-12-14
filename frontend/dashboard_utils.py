"""Utility functions for the Streamlit dashboard.

This module provides data fetching, normalization, and configuration
utilities for the Electrification Progress Tracker dashboard.
"""

from typing import Dict, List, Optional

import pandas as pd
import plotly.colors
import requests
import streamlit as st


def add_global_refresh_button(api_base_url: str):
    """Add a global 'Refresh All Data' button to the sidebar.

    This button clears cache and pre-loads all datasets so they're available
    for all pages without additional API calls.

    Args:
        api_base_url: Base URL for the API to pre-fetch data
    """
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Refresh All Data", width="stretch", type="primary"):
        # Clear cache first
        st.cache_data.clear()

        # Show progress while pre-loading all datasets
        progress_text = "Loading all datasets..."
        progress_bar = st.sidebar.progress(0, text=progress_text)

        # Pre-fetch all datasets to populate cache
        total_datasets = len(AVAILABLE_DATASETS)
        for i, dataset_name in enumerate(AVAILABLE_DATASETS):
            progress_bar.progress(
                (i + 1) / total_datasets, text=f"Loading {dataset_name}..."
            )
            try:
                # Fetch the dataset - this will cache it
                _fetch_dataset_from_api(api_base_url, dataset_name)
            except Exception as e:
                st.sidebar.warning(f"Failed to load {dataset_name}: {e}")

        progress_bar.progress(1.0, text="All data loaded! Reloading page...")
        st.rerun()


def add_page_refresh_button(
    datasets: Optional[List[str]] = None, button_text: str = "🔄 Refresh This Page"
):
    """Add a page-specific refresh button that clears cache for specific datasets.

    This clears cache and reloads the page, re-fetching only the datasets used on this page.

    Args:
        datasets: List of dataset names to clear cache for (if None, clears all)
        button_text: Text to display on the button
    """
    if st.button(button_text, width="stretch"):
        if datasets:
            # Show which datasets are being refreshed
            with st.spinner(f"Refreshing {len(datasets)} dataset(s)..."):
                st.cache_data.clear()
        else:
            st.cache_data.clear()
        st.rerun()


# NZ Region coordinates for mapping (from reflex_demo)
NZ_REGIONS_COORDS = {
    "Northland": {"lat": -35.7, "lon": 174.3},
    "Auckland": {"lat": -36.85, "lon": 174.76},
    "Waikato": {"lat": -37.78, "lon": 175.28},
    "Bay of Plenty": {"lat": -37.69, "lon": 176.17},
    "Gisborne": {"lat": -38.66, "lon": 178.02},
    "Hawkes Bay": {"lat": -39.64, "lon": 176.92},
    "Taranaki": {"lat": -39.35, "lon": 174.08},
    "Manawatu": {"lat": -40.35, "lon": 175.61},
    "Wanganui": {"lat": -39.93, "lon": 175.05},
    "Wellington": {"lat": -41.28, "lon": 174.78},
    "Tasman": {"lat": -41.27, "lon": 172.97},
    "Marlborough": {"lat": -41.51, "lon": 173.96},
    "West Coast": {"lat": -42.45, "lon": 171.21},
    "Canterbury": {"lat": -43.53, "lon": 172.63},
    "Otago": {"lat": -45.03, "lon": 169.4},
    "Southland": {"lat": -46.41, "lon": 168.35},
}

# District to Region mapping for Waka Kotahi MVR data
DISTRICT_TO_REGION = {
    "AUCKLAND": "Auckland",
    "FAR NORTH DISTRICT": "Northland",
    "KAIPARA DISTRICT": "Northland",
    "WHANGAREI DISTRICT": "Northland",
    "HAURAKI DISTRICT": "Waikato",
    "HAMILTON CITY": "Waikato",
    "MATAMATA-PIAKO DISTRICT": "Waikato",
    "OTOROHANGA DISTRICT": "Waikato",
    "SOUTH WAIKATO DISTRICT": "Waikato",
    "THAMES-COROMANDEL DISTRICT": "Waikato",
    "WAIKATO DISTRICT": "Waikato",
    "WAIPA DISTRICT": "Waikato",
    "WAITOMO DISTRICT": "Waikato",
    "KAWERAU DISTRICT": "Bay of Plenty",
    "OPOTIKI DISTRICT": "Bay of Plenty",
    "ROTORUA DISTRICT": "Bay of Plenty",
    "TAURANGA CITY": "Bay of Plenty",
    "WESTERN BAY OF PLENTY DISTRICT": "Bay of Plenty",
    "WHAKATANE DISTRICT": "Bay of Plenty",
    "GISBORNE DISTRICT": "Gisborne",
    "CENTRAL HAWKE'S BAY DISTRICT": "Hawkes Bay",
    "HASTINGS DISTRICT": "Hawkes Bay",
    "NAPIER CITY": "Hawkes Bay",
    "WAIROA DISTRICT": "Hawkes Bay",
    "NEW PLYMOUTH DISTRICT": "Taranaki",
    "SOUTH TARANAKI DISTRICT": "Taranaki",
    "STRATFORD DISTRICT": "Taranaki",
    "HOROWHENUA DISTRICT": "Manawatu",
    "MANAWATU DISTRICT": "Manawatu",
    "PALMERSTON NORTH CITY": "Manawatu",
    "RANGITIKEI DISTRICT": "Manawatu",
    "RUAPEHU DISTRICT": "Manawatu",
    "TARARUA DISTRICT": "Manawatu",
    "WANGANUI DISTRICT": "Wanganui",
    "CARTERTON DISTRICT": "Wellington",
    "KAPITI COAST DISTRICT": "Wellington",
    "LOWER HUTT CITY": "Wellington",
    "MASTERTON DISTRICT": "Wellington",
    "PORIRUA CITY": "Wellington",
    "SOUTH WAIRARAPA DISTRICT": "Wellington",
    "UPPER HUTT CITY": "Wellington",
    "WELLINGTON CITY": "Wellington",
    "GOLDEN BAY DISTRICT": "Tasman",
    "KAIKOURA DISTRICT": "Marlborough",
    "MARLBOROUGH DISTRICT": "Marlborough",
    "NELSON CITY": "Tasman",
    "TASMAN DISTRICT": "Tasman",
    "BULLER DISTRICT": "West Coast",
    "GREY DISTRICT": "West Coast",
    "WESTLAND DISTRICT": "West Coast",
    "ASHBURTON DISTRICT": "Canterbury",
    "CHRISTCHURCH CITY": "Canterbury",
    "HURUNUI DISTRICT": "Canterbury",
    "MACKENZIE DISTRICT": "Canterbury",
    "SELWYN DISTRICT": "Canterbury",
    "TIMARU DISTRICT": "Canterbury",
    "WAIMATE DISTRICT": "Canterbury",
    "WAIMAKARIRI DISTRICT": "Canterbury",
    "CENTRAL OTAGO DISTRICT": "Otago",
    "CLUTHA DISTRICT": "Otago",
    "DUNEDIN CITY": "Otago",
    "QUEENSTOWN-LAKES DISTRICT": "Otago",
    "WAITAKI DISTRICT": "Otago",
    "CATLINS DISTRICT": "Southland",
    "GORE DISTRICT": "Southland",
    "INVERCARGILL CITY": "Southland",
    "SOUTHLAND DISTRICT": "Southland",
    "CHATHAM ISLANDS TERRITORY": "Other",
}

# Region name normalization mapping (GIC -> EMI naming)
REGION_NORMALIZATION = {"Hawke's Bay": "Hawkes Bay", "Manawatu-Whanganui": "Manawatu"}

# Consistent color palette for all charts
CHART_COLORS = plotly.colors.qualitative.Plotly

# All available datasets
AVAILABLE_DATASETS = [
    "eeca_electricity_percentage",
    "eeca_energy_by_fuel",
    "eeca_boiler_energy",
    "gic_analytics",
    "emi_generation_analytics",
    "battery_penetration_commercial",
    "battery_penetration_residential",
    "solar_penetration",
    "battery_capacity",
    "waka_kotahi_ev",
    "waka_kotahi_ff",
    "waka_kotahi_new_ev",
    "waka_kotahi_used_ev",
    "waka_kotahi_fleet_elec",
]


def normalize_region(region: str) -> str:
    """Normalize region names to match EMI conventions.

    Args:
        region: Region name to normalize

    Returns:
        Normalized region name
    """
    return REGION_NORMALIZATION.get(region, region)


def district_to_region(district: str) -> str:
    """Convert Waka Kotahi district names to standard regions.

    Args:
        district: District name from Waka Kotahi data

    Returns:
        Corresponding standard region name
    """
    return DISTRICT_TO_REGION.get(district, district)


def aggregate_districts_to_regions(
    df: pd.DataFrame, region_col: str = "Region"
) -> pd.DataFrame:
    """Aggregate district-level data to region-level.

    Args:
        df: DataFrame with district-level data
        region_col: Name of the region column

    Returns:
        DataFrame with region-level aggregates
    """
    if region_col not in df.columns:
        return df

    # Create region mapping
    df = df.copy()
    df["AggregatedRegion"] = df[region_col].apply(district_to_region)

    # Identify numeric columns to sum
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    # Group by relevant columns and aggregate
    groupby_cols = [
        col
        for col in [
            "Year",
            "Month",
            "Metric_Group",
            "Category",
            "Sub_Category",
            "Fuel_Type",
            "AggregatedRegion",
        ]
        if col in df.columns
    ]

    if not groupby_cols:
        return df

    agg_dict = {col: "sum" for col in numeric_cols if col not in groupby_cols}

    if not agg_dict:
        return df

    df_agg = df.groupby(groupby_cols, dropna=False).agg(agg_dict).reset_index()
    df_agg.rename(columns={"AggregatedRegion": region_col}, inplace=True)

    return df_agg


def calculate_cumulative(
    df: pd.DataFrame, value_col: str, groupby_cols: List[str]
) -> pd.DataFrame:
    """Calculate cumulative sum for time series data.

    Args:
        df: DataFrame with time series data
        value_col: Column to calculate cumulative sum for
        groupby_cols: Columns to group by (e.g., ['Region', 'Category'])

    Returns:
        DataFrame with cumulative column added
    """
    df = df.copy()
    df = df.sort_values(["Year", "Month"] if "Month" in df.columns else ["Year"])
    df[f"{value_col}_cumulative"] = df.groupby(groupby_cols)[value_col].cumsum()
    return df


def calculate_yoy_growth(
    df: pd.DataFrame, value_col: str, groupby_cols: List[str]
) -> pd.DataFrame:
    """Calculate year-over-year growth rate.

    Args:
        df: DataFrame with time series data
        value_col: Column to calculate growth for
        groupby_cols: Columns to group by

    Returns:
        DataFrame with YoY growth column added
    """
    df = df.copy()
    df = df.sort_values(["Year"])
    df[f"{value_col}_yoy"] = df.groupby(groupby_cols)[value_col].pct_change() * 100
    return df


def filter_annual_aggregates(
    df: pd.DataFrame, include_annual: bool = False
) -> pd.DataFrame:
    """Filter out or include annual aggregate rows (Month='Total').

    Args:
        df: DataFrame to filter
        include_annual: Whether to include annual aggregates

    Returns:
        Filtered DataFrame
    """
    if "Month" not in df.columns:
        return df

    if include_annual:
        return df

    # Exclude rows where Month is "Total"
    return df[df["Month"] != "Total"]


def _to_tuple(value):
    """Convert list to tuple for caching, or return None if empty."""
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return tuple(value) if value else None
    return value


@st.cache_data(ttl=3600, show_spinner="Fetching data from API...")
def _fetch_dataset_from_api(
    api_base_url: str,
    dataset: str,
) -> pd.DataFrame:
    """Internal function to fetch full dataset from API (cached by dataset name only).

    This function is cached with minimal parameters to maximize cache reuse across pages.
    Always fetches the complete dataset without any limit.
    Filtering by year, region, limit, etc. is done client-side after fetching.

    Args:
        api_base_url: Base URL for the API
        dataset: Dataset name

    Returns:
        DataFrame with full fetched data
    """
    # Make API request - no limit, fetch all data
    response = requests.get(
        f"{api_base_url}/api/metrics/{dataset}",
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data.get("data", []))

    if df.empty:
        return df

    # Apply client-side normalization (but not filtering - that's done by caller)
    if "Region" in df.columns:
        df["Region"] = df["Region"].apply(normalize_region)

    return df


def fetch_dataset(
    api_base_url: str,
    dataset: str,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    regions: Optional[tuple] = None,
    sectors: Optional[tuple] = None,
    limit: Optional[int] = 1000,
) -> pd.DataFrame:
    """Fetch a single dataset from the backend API with client-side filtering.

    This function fetches the full dataset (cached) then filters/limits client-side.
    This allows cache sharing across pages with different filter parameters.

    Args:
        api_base_url: Base URL for the API
        dataset: Dataset name
        year_min: Minimum year for filtering (applied client-side)
        year_max: Maximum year for filtering (applied client-side)
        regions: Tuple of regions to filter by (applied client-side)
        sectors: Tuple of sectors to filter by (applied client-side)
        limit: Maximum number of rows to return (applied client-side after filtering)

    Returns:
        DataFrame with filtered data
    """
    # Fetch full dataset (this call is cached by dataset name only)
    df = _fetch_dataset_from_api(api_base_url, dataset)

    if df.empty:
        return df

    # Apply client-side year filtering
    if "Year" in df.columns:
        if year_min is not None:
            df = df[df["Year"] >= year_min]
        if year_max is not None:
            df = df[df["Year"] <= year_max]

    # Filter by regions if specified
    if regions and "All" not in regions and "Region" in df.columns:
        df = df[df["Region"].isin(regions)]

    # Filter by sectors if specified
    if sectors and "All" not in sectors:
        if "Sub-Category" in df.columns:
            df = df[df["Sub-Category"].isin(sectors)]
        elif "Sub_Category" in df.columns:
            df = df[df["Sub_Category"].isin(sectors)]

    # Apply limit client-side (after all filtering)
    if limit is not None and len(df) > limit:
        df = df.head(limit)

    return df


def fetch_all_datasets(
    api_base_url: str,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    regions: Optional[tuple] = None,
    sectors: Optional[tuple] = None,
    load_all: bool = False,
) -> Dict[str, pd.DataFrame]:
    """Fetch all datasets from the backend API with client-side filtering.

    This function fetches full datasets (cached) then filters client-side.
    This allows cache sharing across pages with different filter parameters.

    Args:
        api_base_url: Base URL for the API
        year_min: Minimum year for filtering (applied client-side)
        year_max: Maximum year for filtering (applied client-side)
        regions: Tuple of regions to filter by (applied client-side)
        sectors: Tuple of sectors to filter by (applied client-side)
        load_all: Whether to load all data (no pagination)

    Returns:
        Dictionary mapping dataset names to DataFrames
    """
    limit = None if load_all else 100000  # Increased limit for full dataset fetching

    datasets = {}
    for dataset_name in AVAILABLE_DATASETS:
        try:
            df = fetch_dataset(
                api_base_url,
                dataset_name,
                year_min,
                year_max,
                regions,
                sectors,
                limit,
            )
            datasets[dataset_name] = df
        except Exception as e:
            st.warning(f"Could not fetch {dataset_name}: {e}")
            datasets[dataset_name] = pd.DataFrame()

    return datasets


def get_latest_kpi_value(df: pd.DataFrame, value_col: str) -> tuple[float, float]:
    """Get the latest KPI value and calculate delta from previous period.

    Args:
        df: DataFrame with Year column and value column
        value_col: Name of the column containing values

    Returns:
        Tuple of (latest_value, delta_from_previous)
    """
    if df.empty or value_col not in df.columns or "Year" not in df.columns:
        return 0.0, 0.0

    # Sort by year and get latest
    df_sorted = df.sort_values("Year")

    if len(df_sorted) == 0:
        return 0.0, 0.0

    latest = df_sorted.iloc[-1][value_col]

    if len(df_sorted) < 2:
        return float(latest), 0.0

    previous = df_sorted.iloc[-2][value_col]
    delta = float(latest - previous)

    return float(latest), delta


def normalize_to_0_100(series: pd.Series) -> pd.Series:
    """Normalize a series to 0-100 scale for comparison charts.

    Args:
        series: Series to normalize

    Returns:
        Normalized series
    """
    min_val = series.min()
    max_val = series.max()

    if max_val == min_val:
        return pd.Series([50.0] * len(series), index=series.index)

    return 100 * (series - min_val) / (max_val - min_val)


def create_paginated_dataframe(
    df: pd.DataFrame, page_size: int = 100, page_key: str = "page_number"
) -> pd.DataFrame:
    """Create a paginated view of a DataFrame using Streamlit session state.

    Args:
        df: DataFrame to paginate
        page_size: Number of rows per page
        page_key: Unique key for page number in session state

    Returns:
        Paginated DataFrame slice
    """
    if page_key not in st.session_state:
        st.session_state[page_key] = 0

    total_pages = max(1, len(df) // page_size + (1 if len(df) % page_size > 0 else 0))

    # Ensure page number is within valid range
    if st.session_state[page_key] >= total_pages:
        st.session_state[page_key] = max(0, total_pages - 1)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if (
            st.button("← Previous", key=f"prev_{page_key}")
            and st.session_state[page_key] > 0
        ):
            st.session_state[page_key] -= 1
            st.rerun()

    with col2:
        st.write(
            f"Page {st.session_state[page_key] + 1} of {total_pages} ({len(df):,} total rows)"
        )

    with col3:
        if (
            st.button("Next →", key=f"next_{page_key}")
            and st.session_state[page_key] < total_pages - 1
        ):
            st.session_state[page_key] += 1
            st.rerun()

    start_idx = st.session_state[page_key] * page_size
    end_idx = min(start_idx + page_size, len(df))

    return df.iloc[start_idx:end_idx]
