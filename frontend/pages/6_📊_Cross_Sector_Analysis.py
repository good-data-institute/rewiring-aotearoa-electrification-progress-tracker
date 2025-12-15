"""Cross-Sector Analysis - Correlations and Trends.

This page shows normalized trends and correlation analysis across metrics.
"""

import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard_utils import (
    AVAILABLE_DATASETS,
    CHART_COLORS,
    add_global_refresh_button,
    add_page_refresh_button,
    fetch_all_datasets,
    filter_annual_aggregates,
    normalize_to_0_100,
)

load_dotenv()

BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
API_BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

st.set_page_config(page_title="Cross-Sector Analysis", page_icon="📊", layout="wide")

st.title("📊 Cross-Sector Analysis")
st.markdown(
    "**Normalized trends and correlation analysis across all electrification metrics**"
)

st.sidebar.header("🔍 Filters")

# Add global refresh button
add_global_refresh_button(API_BASE_URL)

year_range = st.sidebar.slider("Year Range", 2015, 2025, (2018, 2025))

with st.spinner("Loading data..."):
    datasets = fetch_all_datasets(
        API_BASE_URL, year_range[0], year_range[1], load_all=False
    )
    for key in datasets:
        datasets[key] = filter_annual_aggregates(datasets[key], False)

# Add page-specific refresh button (all datasets)
add_page_refresh_button(datasets=AVAILABLE_DATASETS)

# Normalized Timeline
st.subheader("Normalized Multi-Metric Timeline (0-100 Scale)")

normalized_data = []

# Fleet electrification
df_fleet = datasets.get("waka_kotahi_fleet_elec", pd.DataFrame())
if (
    not df_fleet.empty
    and "_05_P1_FleetElec" in df_fleet.columns
    and "Year" in df_fleet.columns
):
    df_norm = df_fleet.groupby("Year")["_05_P1_FleetElec"].mean().reset_index()
    if len(df_norm) > 1:
        df_norm["value"] = normalize_to_0_100(df_norm["_05_P1_FleetElec"])
        df_norm["metric"] = "Fleet Electrification"
        normalized_data.append(df_norm[["Year", "value", "metric"]])

# Electricity share
df_elec = datasets.get("eeca_electricity_percentage", pd.DataFrame())
if (
    not df_elec.empty
    and "_13_P1_ElecCons" in df_elec.columns
    and "Year" in df_elec.columns
):
    df_norm = df_elec.groupby("Year")["_13_P1_ElecCons"].mean().reset_index()
    if len(df_norm) > 1:
        df_norm["value"] = normalize_to_0_100(df_norm["_13_P1_ElecCons"])
        df_norm["metric"] = "Electricity Share"
        normalized_data.append(df_norm[["Year", "value", "metric"]])

# Renewable
df_renewable = datasets.get("emi_generation_analytics", pd.DataFrame())
if (
    not df_renewable.empty
    and "_12_P1_EnergyRenew" in df_renewable.columns
    and "Year" in df_renewable.columns
):
    df_norm = df_renewable.groupby("Year")["_12_P1_EnergyRenew"].mean().reset_index()
    if len(df_norm) > 1:
        df_norm["value"] = normalize_to_0_100(df_norm["_12_P1_EnergyRenew"])
        df_norm["metric"] = "Renewable Generation"
        normalized_data.append(df_norm[["Year", "value", "metric"]])

# Battery
df_battery = datasets.get("battery_penetration_residential", pd.DataFrame())
if (
    not df_battery.empty
    and "_06b_P1_BattPen" in df_battery.columns
    and "Year" in df_battery.columns
):
    df_norm = df_battery.groupby("Year")["_06b_P1_BattPen"].mean().reset_index()
    if len(df_norm) > 1:
        df_norm["value"] = normalize_to_0_100(df_norm["_06b_P1_BattPen"])
        df_norm["metric"] = "Battery Penetration"
        normalized_data.append(df_norm[["Year", "value", "metric"]])

# Gas (inverted)
df_gas = datasets.get("gic_analytics", pd.DataFrame())
if not df_gas.empty and "_10_P1_Gas" in df_gas.columns and "Year" in df_gas.columns:
    df_norm = df_gas.groupby("Year")["_10_P1_Gas"].sum().reset_index()
    if len(df_norm) > 1:
        df_norm["value"] = 100 - normalize_to_0_100(df_norm["_10_P1_Gas"])
        df_norm["metric"] = "Gas Decline (inverted)"
        normalized_data.append(df_norm[["Year", "value", "metric"]])

# Solar
df_solar = datasets.get("solar_penetration", pd.DataFrame())
if (
    not df_solar.empty
    and "_07_P1_Sol" in df_solar.columns
    and "Year" in df_solar.columns
):
    df_norm = df_solar.groupby("Year")["_07_P1_Sol"].sum().reset_index()
    if len(df_norm) > 1:
        df_norm["value"] = normalize_to_0_100(df_norm["_07_P1_Sol"])
        df_norm["metric"] = "Solar Capacity"
        normalized_data.append(df_norm[["Year", "value", "metric"]])

if normalized_data:
    df_all_normalized = pd.concat(normalized_data, ignore_index=True)
    fig = px.line(
        df_all_normalized,
        x="Year",
        y="value",
        color="metric",
        markers=True,
        labels={"value": "Normalized Value (0-100)"},
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, width="stretch")
else:
    st.info("Insufficient data for normalized comparison")

st.markdown("---")

# Correlation Matrix
st.subheader("Metric Correlation Matrix")

corr_data = {}

if (
    not df_elec.empty
    and "_13_P1_ElecCons" in df_elec.columns
    and "Year" in df_elec.columns
):
    corr_data["Electricity %"] = df_elec.groupby("Year")["_13_P1_ElecCons"].mean()

if (
    not df_renewable.empty
    and "_12_P1_EnergyRenew" in df_renewable.columns
    and "Year" in df_renewable.columns
):
    corr_data["Renewable %"] = (
        df_renewable.groupby("Year")["_12_P1_EnergyRenew"].mean() * 100
    )

if (
    not df_battery.empty
    and "_06b_P1_BattPen" in df_battery.columns
    and "Year" in df_battery.columns
):
    corr_data["Battery %"] = df_battery.groupby("Year")["_06b_P1_BattPen"].mean()

if not df_gas.empty and "_10_P1_Gas" in df_gas.columns and "Year" in df_gas.columns:
    corr_data["Gas Connections"] = df_gas.groupby("Year")["_10_P1_Gas"].sum()

if (
    not df_fleet.empty
    and "_05_P1_FleetElec" in df_fleet.columns
    and "Year" in df_fleet.columns
):
    corr_data["Fleet Elec %"] = df_fleet.groupby("Year")["_05_P1_FleetElec"].mean()

if len(corr_data) >= 2:
    df_corr = pd.DataFrame(corr_data)
    corr_matrix = df_corr.corr()

    fig = px.imshow(
        corr_matrix,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        aspect="auto",
        zmin=-1,
        zmax=1,
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, width="stretch")

    st.info(
        "💡 **Interpretation**: Positive correlation (blue) means metrics move together. "
        "Negative correlation (red) means metrics move in opposite directions."
    )
else:
    st.info("Need at least 2 metrics with overlapping years for correlation analysis")

st.caption(
    "📊 Use this page to understand relationships between different electrification indicators"
)
