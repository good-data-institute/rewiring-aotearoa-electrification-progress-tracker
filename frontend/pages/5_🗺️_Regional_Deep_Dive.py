"""Regional Deep Dive - Interactive Regional Comparison.

This page provides detailed regional analysis with interactive maps and comparisons.
"""

import os
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard_utils import (
    AVAILABLE_DATASETS,
    NZ_REGIONS_COORDS,
    add_global_refresh_button,
    add_page_refresh_button,
    fetch_all_datasets,
    filter_annual_aggregates,
)


load_dotenv()

BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
API_BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

st.set_page_config(page_title="Regional Analysis", page_icon="🗺️", layout="wide")

st.title("🗺️ Regional Deep Dive")
st.markdown("**Interactive regional comparison across all metrics**")

st.sidebar.header("🔍 Filters")

# Add global refresh button
add_global_refresh_button(API_BASE_URL)

year_range = st.sidebar.slider("Year Range", 2015, 2025, (2020, 2025))

# Fetch data
with st.spinner("Loading regional data..."):
    datasets = fetch_all_datasets(
        API_BASE_URL, year_range[0], year_range[1], load_all=False
    )
    for key in datasets:
        datasets[key] = filter_annual_aggregates(datasets[key], False)

# Add page-specific refresh button (all datasets)
add_page_refresh_button(datasets=AVAILABLE_DATASETS)

# Interactive Map
st.subheader("Interactive Regional Map")

map_metric = st.radio(
    "Select Metric to Display",
    options=[
        "Renewable Energy %",
        "Gas Connections",
        "Battery Penetration",
        "Fleet Electrification %",
    ],
    horizontal=True,
)

# Prepare map data
if map_metric == "Renewable Energy %":
    df_map = datasets.get("emi_generation_analytics", pd.DataFrame())
    if (
        not df_map.empty
        and "Region" in df_map.columns
        and "_12_P1_EnergyRenew" in df_map.columns
    ):
        df_map_agg = df_map.groupby("Region")["_12_P1_EnergyRenew"].mean().reset_index()
        # Normalize to percent only if the data looks like a 0-1 fraction
        renewable_max = df_map_agg["_12_P1_EnergyRenew"].max()
        if renewable_max <= 1.2:
            df_map_agg["value"] = df_map_agg["_12_P1_EnergyRenew"] * 100
        else:
            df_map_agg["value"] = df_map_agg["_12_P1_EnergyRenew"]
        df_map_agg["lat"] = df_map_agg["Region"].map(
            lambda r: NZ_REGIONS_COORDS.get(r, {}).get("lat")
        )
        df_map_agg["lon"] = df_map_agg["Region"].map(
            lambda r: NZ_REGIONS_COORDS.get(r, {}).get("lon")
        )
        df_map_agg = df_map_agg.dropna(subset=["lat", "lon"])
        if not df_map_agg.empty:
            value_min = df_map_agg["value"].min()
            value_max = df_map_agg["value"].max()
            if value_max == value_min:
                df_map_agg["marker_size"] = 18
            else:
                df_map_agg["marker_size"] = (
                    8
                    + ((df_map_agg["value"] - value_min) / (value_max - value_min)) * 22
                )

        fig = go.Figure(
            data=go.Scattergeo(
                lon=df_map_agg["lon"],
                lat=df_map_agg["lat"],
                text=df_map_agg["Region"],
                mode="markers",
                marker=dict(
                    size=df_map_agg["marker_size"],
                    color=df_map_agg["value"],
                    colorscale="Greens",
                    showscale=True,
                    colorbar=dict(title="Renewable %"),
                ),
                hovertemplate="<b>%{text}</b><br>%{marker.color:.1f}%<extra></extra>",
            )
        )
        fig.update_geos(center=dict(lon=173, lat=-41), projection_scale=15)
        st.plotly_chart(fig, use_container_width=True)

elif map_metric == "Fleet Electrification %":
    df_map = datasets.get("waka_kotahi_fleet_elec", pd.DataFrame())
    if (
        not df_map.empty
        and "Region" in df_map.columns
        and "_05_P1_FleetElec" in df_map.columns
    ):
        df_map_agg = df_map.groupby("Region")["_05_P1_FleetElec"].mean().reset_index()
        df_map_agg["lat"] = df_map_agg["Region"].map(
            lambda r: NZ_REGIONS_COORDS.get(r, {}).get("lat")
        )
        df_map_agg["lon"] = df_map_agg["Region"].map(
            lambda r: NZ_REGIONS_COORDS.get(r, {}).get("lon")
        )
        df_map_agg = df_map_agg.dropna(subset=["lat", "lon"])

        fig = go.Figure(
            data=go.Scattergeo(
                lon=df_map_agg["lon"],
                lat=df_map_agg["lat"],
                text=df_map_agg["Region"],
                mode="markers",
                marker=dict(
                    size=df_map_agg["_05_P1_FleetElec"] * 5,
                    color=df_map_agg["_05_P1_FleetElec"],
                    colorscale="Blues",
                    showscale=True,
                ),
                hovertemplate="<b>%{text}</b><br>%{marker.color:.2f}%<extra></extra>",
            )
        )
        fig.update_geos(center=dict(lon=173, lat=-41), projection_scale=15)
        st.plotly_chart(fig, width="stretch")

st.markdown("---")

# Regional Comparison Table
st.subheader("Regional Performance Matrix")

regional_metrics = []

# Collect metrics
for dataset_name, metric_col, label in [
    ("emi_generation_analytics", "_12_P1_EnergyRenew", "Renewable %"),
    ("gic_analytics", "_10_P1_Gas", "Gas Connections"),
    ("battery_penetration_residential", "_06b_P1_BattPen", "Battery %"),
    ("waka_kotahi_fleet_elec", "_05_P1_FleetElec", "Fleet Elec %"),
]:
    df = datasets.get(dataset_name, pd.DataFrame())
    if not df.empty and "Region" in df.columns and metric_col in df.columns:
        agg_func = (
            "mean" if "%" in label or "Elec" in label or "Renewable" in label else "sum"
        )
        df_agg = df.groupby("Region")[metric_col].agg(agg_func).reset_index()
        df_agg.columns = ["Region", label]
        if "Renewable" in label:
            df_agg[label] *= 100
        regional_metrics.append(df_agg)

if regional_metrics:
    df_regional = regional_metrics[0]
    for df in regional_metrics[1:]:
        df_regional = df_regional.merge(df, on="Region", how="outer")
    st.dataframe(df_regional.sort_values("Region"), width="stretch")
else:
    st.info("No regional data available")

st.caption("🗺️ Use interactive map and table to compare regional performance")
