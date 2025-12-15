"""Energy Grid - Renewable Generation and Electricity Consumption.

This page shows electricity generation mix and renewable energy metrics.
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

st.set_page_config(
    page_title="Energy Grid - Electrification Tracker",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ Energy Grid & Renewable Generation")
st.markdown("**Electricity generation, consumption, and renewable energy analysis**")

# Sidebar
st.sidebar.header("🔍 Filters")

# Add global refresh button
add_global_refresh_button(API_BASE_URL)

year_range = st.sidebar.slider(
    "Year Range",
    min_value=2015,
    max_value=2025,
    value=(2020, 2025),
)

include_annual = st.sidebar.checkbox("Include Annual Aggregates", value=False)

# Fetch data
with st.spinner("Loading energy data..."):
    datasets = {}
    for dataset_name in [
        "eeca_electricity_percentage",
        "eeca_energy_by_fuel",
        "emi_generation_analytics",
    ]:
        try:
            df = fetch_dataset(
                API_BASE_URL,
                dataset_name,
                year_min=year_range[0],
                year_max=year_range[1],
                limit=10000,
            )
            df = filter_annual_aggregates(df, include_annual)
            datasets[dataset_name] = df
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
            datasets[dataset_name] = pd.DataFrame()

# Add page-specific refresh button
ENERGY_DATASETS = [
    "eeca_electricity_percentage",
    "eeca_energy_by_fuel",
    "emi_generation_analytics",
]
add_page_refresh_button(datasets=ENERGY_DATASETS)

# KPIs
st.subheader("Key Energy Metrics")
kpi_cols = st.columns(3)

with kpi_cols[0]:
    df_elec = datasets.get("eeca_electricity_percentage", pd.DataFrame())
    if not df_elec.empty and "_13_P1_ElecCons" in df_elec.columns:
        latest, delta = get_latest_kpi_value(df_elec, "_13_P1_ElecCons")
        st.metric(
            "Electricity Share",
            f"{latest:.1f}%",
            f"{delta:+.1f}%",
            help="Electricity's share of total energy",
        )
    else:
        st.metric("Electricity Share", "N/A")

with kpi_cols[1]:
    df_renewable = datasets.get("emi_generation_analytics", pd.DataFrame())
    if not df_renewable.empty and "_12_P1_EnergyRenew" in df_renewable.columns:
        df_renewable["renewable_pct"] = df_renewable["_12_P1_EnergyRenew"] * 100
        latest, delta = get_latest_kpi_value(df_renewable, "renewable_pct")
        st.metric(
            "Renewable Generation",
            f"{latest:.1f}%",
            f"{delta:+.1f}%",
            help="Renewable % of electricity generation",
        )
    else:
        st.metric("Renewable Generation", "N/A")

with kpi_cols[2]:
    df_fuel = datasets.get("eeca_energy_by_fuel", pd.DataFrame())
    if not df_fuel.empty and "_14_P1_EnergyxFuel" in df_fuel.columns:
        if "Year" in df_fuel.columns:
            latest_year = df_fuel["Year"].max()
            total_energy = df_fuel[df_fuel["Year"] == latest_year][
                "_14_P1_EnergyxFuel"
            ].sum()
            st.metric(
                "Total Energy",
                f"{total_energy / 1000:.1f} GWh",
                help="Total energy consumption",
            )
    else:
        st.metric("Total Energy", "N/A")

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Electricity Share Trend")
    df_elec = datasets.get("eeca_electricity_percentage", pd.DataFrame())
    if (
        not df_elec.empty
        and "_13_P1_ElecCons" in df_elec.columns
        and "Year" in df_elec.columns
    ):
        fig = px.line(
            df_elec,
            x="Year",
            y="_13_P1_ElecCons",
            markers=True,
            labels={"_13_P1_ElecCons": "Electricity %"},
            color_discrete_sequence=["#3498db"],
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No data available")

with col2:
    st.subheader("Renewable Energy by Region")
    df_renewable = datasets.get("emi_generation_analytics", pd.DataFrame())
    if not df_renewable.empty and "_12_P1_EnergyRenew" in df_renewable.columns:
        df_renewable["renewable_pct"] = df_renewable["_12_P1_EnergyRenew"] * 100
        if "Region" in df_renewable.columns:
            fig = px.box(
                df_renewable,
                x="Region",
                y="renewable_pct",
                labels={"renewable_pct": "Renewable %"},
                color_discrete_sequence=CHART_COLORS,
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No regional data")
    else:
        st.info("No data available")

st.subheader("Energy Consumption by Fuel Type")
df_fuel = datasets.get("eeca_energy_by_fuel", pd.DataFrame())
if not df_fuel.empty and "_14_P1_EnergyxFuel" in df_fuel.columns:
    if "Category" in df_fuel.columns and "Year" in df_fuel.columns:
        df_fuel_agg = (
            df_fuel.groupby(["Year", "Category"])["_14_P1_EnergyxFuel"]
            .sum()
            .reset_index()
        )
        fig = px.area(
            df_fuel_agg,
            x="Year",
            y="_14_P1_EnergyxFuel",
            color="Category",
            labels={"_14_P1_EnergyxFuel": "Energy (MWh)"},
            color_discrete_sequence=CHART_COLORS,
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Missing required columns")
else:
    st.info("No fuel data available")

st.markdown("---")

# Renewable by Month Heatmap
st.subheader("Renewable Generation Patterns")
df_renewable = datasets.get("emi_generation_analytics", pd.DataFrame())
if not df_renewable.empty and "_12_P1_EnergyRenew" in df_renewable.columns:
    if "Month" in df_renewable.columns and "Year" in df_renewable.columns:
        df_heatmap = df_renewable.pivot_table(
            values="_12_P1_EnergyRenew", index="Month", columns="Year", aggfunc="mean"
        )
        df_heatmap = df_heatmap * 100
        fig = px.imshow(
            df_heatmap,
            labels=dict(color="Renewable %"),
            color_continuous_scale="Greens",
            aspect="auto",
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Missing month/year columns")
else:
    st.info("No renewable data")

st.caption("💡 Navigate to other pages for sector-specific energy analysis")
