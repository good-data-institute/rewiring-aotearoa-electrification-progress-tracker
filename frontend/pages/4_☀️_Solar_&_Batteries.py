"""Solar & Batteries - Distributed Energy Resources.

This page shows solar and battery adoption metrics.
"""

import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard_utils import (
    CHART_COLORS,
    add_global_refresh_button,
    add_page_refresh_button,
    fetch_dataset,
    filter_annual_aggregates,
    get_latest_kpi_value,
)

load_dotenv()

BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
API_BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

st.set_page_config(page_title="Solar & Batteries", page_icon="☀️", layout="wide")

st.title("☀️ Solar & Battery Adoption")
st.markdown("**Distributed energy resources and battery storage analysis**")

st.sidebar.header("🔍 Filters")

# Add global refresh button
add_global_refresh_button(API_BASE_URL)

year_range = st.sidebar.slider("Year Range", 2013, 2025, (2018, 2025))
include_annual = st.sidebar.checkbox("Include Annual Aggregates", False)

with st.spinner("Loading solar & battery data..."):
    datasets = {}
    for dataset_name in [
        "battery_penetration_commercial",
        "battery_penetration_residential",
        "solar_penetration",
        "battery_capacity",
    ]:
        try:
            df = fetch_dataset(
                API_BASE_URL, dataset_name, year_range[0], year_range[1], limit=20000
            )
            df = filter_annual_aggregates(df, include_annual)
            datasets[dataset_name] = df
        except Exception:
            datasets[dataset_name] = pd.DataFrame()

# Add page-specific refresh button
SOLAR_DATASETS = [
    "battery_penetration_commercial",
    "battery_penetration_residential",
    "solar_penetration",
    "battery_capacity",
]
add_page_refresh_button(datasets=SOLAR_DATASETS)

# KPIs
kpi_cols = st.columns(4)

with kpi_cols[0]:
    df_solar = datasets.get("solar_penetration", pd.DataFrame())
    if not df_solar.empty and "_07_P1_Sol" in df_solar.columns:
        latest_year = df_solar["Year"].max() if "Year" in df_solar.columns else None
        if latest_year:
            total_solar = df_solar[df_solar["Year"] == latest_year]["_07_P1_Sol"].sum()
            st.metric("Solar Capacity", f"{total_solar:.1f} MW")

with kpi_cols[1]:
    df_battery = datasets.get("battery_capacity", pd.DataFrame())
    if not df_battery.empty and "_08_P1_Batt" in df_battery.columns:
        latest_year = df_battery["Year"].max() if "Year" in df_battery.columns else None
        if latest_year:
            total_battery = df_battery[df_battery["Year"] == latest_year][
                "_08_P1_Batt"
            ].sum()
            st.metric("Battery Capacity", f"{total_battery:.1f} MW")

with kpi_cols[2]:
    df_batt_pen = datasets.get("battery_penetration_residential", pd.DataFrame())
    if not df_batt_pen.empty and "_06b_P1_BattPen" in df_batt_pen.columns:
        latest, delta = get_latest_kpi_value(df_batt_pen, "_06b_P1_BattPen")
        st.metric("Battery Penetration", f"{latest:.1f}%", f"{delta:+.1f}%")

with kpi_cols[3]:
    df_batt_solar = datasets.get("battery_penetration_commercial", pd.DataFrame())
    if not df_batt_solar.empty and "_06a_P1_BattPen" in df_batt_solar.columns:
        latest, delta = get_latest_kpi_value(df_batt_solar, "_06a_P1_BattPen")
        st.metric("Solar+Battery %", f"{latest:.1f}%", f"{delta:+.1f}%")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Solar Capacity Growth")
    df_solar = datasets.get("solar_penetration", pd.DataFrame())
    if (
        not df_solar.empty
        and "_07_P1_Sol" in df_solar.columns
        and "Year" in df_solar.columns
    ):
        df_solar_agg = df_solar.groupby("Year")["_07_P1_Sol"].sum().reset_index()
        fig = px.area(
            df_solar_agg,
            x="Year",
            y="_07_P1_Sol",
            labels={"_07_P1_Sol": "Solar Capacity (MW)"},
            color_discrete_sequence=["#f39c12"],
        )
        st.plotly_chart(fig, width="stretch")

with col2:
    st.subheader("Battery Adoption Curve")
    df_batt = datasets.get("battery_penetration_residential", pd.DataFrame())
    if (
        not df_batt.empty
        and "_06b_P1_BattPen" in df_batt.columns
        and "Year" in df_batt.columns
    ):
        df_batt_agg = df_batt.groupby("Year")["_06b_P1_BattPen"].mean().reset_index()
        fig = px.line(
            df_batt_agg,
            x="Year",
            y="_06b_P1_BattPen",
            markers=True,
            labels={"_06b_P1_BattPen": "Battery Penetration %"},
            color_discrete_sequence=["#9b59b6"],
        )
        st.plotly_chart(fig, width="stretch")

st.subheader("Solar & Battery by Sector")
df_solar = datasets.get("solar_penetration", pd.DataFrame())
if not df_solar.empty and "_07_P1_Sol" in df_solar.columns:
    if "Sub-Category" in df_solar.columns and "Year" in df_solar.columns:
        df_solar_agg = (
            df_solar.groupby(["Year", "Sub-Category"])["_07_P1_Sol"]
            .mean()
            .reset_index()
        )
        fig = px.line(
            df_solar_agg,
            x="Year",
            y="_07_P1_Sol",
            color="Sub-Category",
            markers=True,
            labels={"_07_P1_Sol": "Solar (MW)"},
            color_discrete_sequence=CHART_COLORS,
        )
        st.plotly_chart(fig, width="stretch")

st.caption(
    "☀️ Solar and battery adoption shows progress in distributed energy resources"
)
