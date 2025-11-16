"""Utility functions for the Streamlit dashboard.

This module provides data fetching, normalization, and configuration
utilities for the Electrification Progress Tracker dashboard.
"""

import json
from typing import Dict, List, Optional

import pandas as pd
import plotly.colors
import requests
import streamlit as st

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

# Region name normalization mapping (GIC -> EMI naming)
REGION_NORMALIZATION = {"Hawke's Bay": "Hawkes Bay", "Manawatu-Whanganui": "Manawatu"}

# Consistent color palette for all charts
CHART_COLORS = plotly.colors.qualitative.Plotly

# All available datasets
AVAILABLE_DATASETS = [
    "eeca_electricity_percentage",
    "eeca_energy_by_fuel",
    "gic_analytics",
    "emi_generation_analytics",
    "battery_penetration_commercial",
    "battery_penetration_residential",
    "solar_penetration",
]


def normalize_region(region: str) -> str:
    """Normalize region names to match EMI conventions.

    Args:
        region: Region name to normalize

    Returns:
        Normalized region name
    """
    return REGION_NORMALIZATION.get(region, region)


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


@st.cache_data(ttl=3600)
def fetch_dataset(
    api_base_url: str,
    dataset: str,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    regions: Optional[List[str]] = None,
    sectors: Optional[List[str]] = None,
    limit: Optional[int] = 1000,
) -> pd.DataFrame:
    """Fetch a single dataset from the backend API with filters.

    Args:
        api_base_url: Base URL for the API
        dataset: Dataset name
        year_min: Minimum year for filtering
        year_max: Maximum year for filtering
        regions: List of regions to filter by
        sectors: List of sectors to filter by
        limit: Maximum number of rows (None for all data)

    Returns:
        DataFrame with fetched data
    """
    # Build filter JSON
    filters = {}

    if year_min is not None and year_max is not None:
        filters["Year"] = {"gte": year_min, "lte": year_max}
    elif year_min is not None:
        filters["Year"] = {"gte": year_min}
    elif year_max is not None:
        filters["Year"] = {"lte": year_max}

    # Build request parameters
    params = {}
    if filters:
        params["filter_json"] = json.dumps(filters)
    if limit is not None:
        params["limit"] = limit

    # Make API request
    response = requests.get(
        f"{api_base_url}/api/metrics/{dataset}",
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame(data.get("data", []))

    if df.empty:
        return df

    # Apply client-side normalization and filters
    if "Region" in df.columns:
        df["Region"] = df["Region"].apply(normalize_region)

        # Filter by regions if specified
        if regions and "All" not in regions:
            df = df[df["Region"].isin(regions)]

    # Filter by sectors if specified
    if sectors and "All" not in sectors and "Sub-Category" in df.columns:
        df = df[df["Sub-Category"].isin(sectors)]

    return df


@st.cache_data(ttl=3600)
def fetch_all_datasets(
    api_base_url: str,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    regions: Optional[List[str]] = None,
    sectors: Optional[List[str]] = None,
    load_all: bool = False,
) -> Dict[str, pd.DataFrame]:
    """Fetch all datasets from the backend API with filters.

    Args:
        api_base_url: Base URL for the API
        year_min: Minimum year for filtering
        year_max: Maximum year for filtering
        regions: List of regions to filter by
        sectors: List of sectors to filter by
        load_all: Whether to load all data (no pagination)

    Returns:
        Dictionary mapping dataset names to DataFrames
    """
    limit = None if load_all else 1000

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
