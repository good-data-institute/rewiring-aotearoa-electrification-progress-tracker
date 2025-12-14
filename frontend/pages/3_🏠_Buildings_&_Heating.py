"""Buildings & Heating - Gas Connections and Boiler Energy.

This page shows gas connection trends and fossil fuel boiler energy consumption.
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
    page_title="Buildings & Heating - Electrification Tracker",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 Buildings & Heating")
st.markdown("**Gas connections and heating energy consumption analysis**")

# Sidebar
st.sidebar.header("🔍 Filters")

# Add global refresh button
add_global_refresh_button(API_BASE_URL)

year_range = st.sidebar.slider("Year Range", 2015, 2025, (2018, 2025))
include_annual = st.sidebar.checkbox("Include Annual Aggregates", False)

# Fetch data
with st.spinner("Loading buildings data..."):
    datasets = {}
    for dataset_name in ["gic_analytics", "eeca_boiler_energy", "eeca_energy_by_fuel"]:
        try:
            df = fetch_dataset(
                API_BASE_URL, dataset_name, year_range[0], year_range[1], limit=10000
            )
            df = filter_annual_aggregates(df, include_annual)
            datasets[dataset_name] = df
        except Exception:
            datasets[dataset_name] = pd.DataFrame()

# Add page-specific refresh button
BUILDINGS_DATASETS = ["gic_analytics", "eeca_boiler_energy", "eeca_energy_by_fuel"]
add_page_refresh_button(datasets=BUILDINGS_DATASETS)

# KPIs
kpi_cols = st.columns(3)

with kpi_cols[0]:
    df_gas = datasets.get("gic_analytics", pd.DataFrame())
    if not df_gas.empty and "_10_P1_Gas" in df_gas.columns:
        latest, delta = get_latest_kpi_value(df_gas, "_10_P1_Gas")
        st.metric(
            "New Gas Connections",
            f"{int(latest)}",
            f"{int(delta):+d}",
            delta_color="inverse",
            help="Lower is better",
        )

with kpi_cols[1]:
    df_boiler = datasets.get("eeca_boiler_energy", pd.DataFrame())
    if not df_boiler.empty and "_11_P1_EnergyFF" in df_boiler.columns:
        latest, delta = get_latest_kpi_value(df_boiler, "_11_P1_EnergyFF")
        st.metric(
            "Fossil Boiler Energy",
            f"{latest/1000:.1f} GWh",
            f"{delta/1000:+.1f} GWh",
            delta_color="inverse",
            help="Fossil fuel energy for boilers",
        )

with kpi_cols[2]:
    if not df_gas.empty and "_10_P1_Gas" in df_gas.columns and "Year" in df_gas.columns:
        years = df_gas["Year"].unique()
        if len(years) >= 2:
            first_year = min(years)
            last_year = max(years)
            first_val = df_gas[df_gas["Year"] == first_year]["_10_P1_Gas"].sum()
            last_val = df_gas[df_gas["Year"] == last_year]["_10_P1_Gas"].sum()
            decline = ((first_val - last_val) / first_val * 100) if first_val > 0 else 0
            st.metric(
                "Gas Decline Rate",
                f"{decline:.1f}%",
                help=f"Decline from {first_year} to {last_year}",
            )

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Gas Connections Trend")
    df_gas = datasets.get("gic_analytics", pd.DataFrame())
    if not df_gas.empty and "_10_P1_Gas" in df_gas.columns and "Year" in df_gas.columns:
        df_gas_agg = df_gas.groupby("Year")["_10_P1_Gas"].sum().reset_index()
        fig = px.line(
            df_gas_agg,
            x="Year",
            y="_10_P1_Gas",
            markers=True,
            labels={"_10_P1_Gas": "New Connections"},
            color_discrete_sequence=["#e74c3c"],
        )
        st.plotly_chart(fig, width="stretch")

with col2:
    st.subheader("Boiler Energy by Sector")
    df_boiler = datasets.get("eeca_boiler_energy", pd.DataFrame())
    if not df_boiler.empty and "_11_P1_EnergyFF" in df_boiler.columns:
        if "Sub-Category" in df_boiler.columns and "Year" in df_boiler.columns:
            fig = px.bar(
                df_boiler,
                x="Year",
                y="_11_P1_EnergyFF",
                color="Sub-Category",
                labels={"_11_P1_EnergyFF": "Energy (MWh)"},
                color_discrete_sequence=CHART_COLORS,
            )
            st.plotly_chart(fig, width="stretch")

st.subheader("Heating Fuel Transition")
df_fuel = datasets.get("eeca_energy_by_fuel", pd.DataFrame())
if not df_fuel.empty and "_14_P1_EnergyxFuel" in df_fuel.columns:
    heating_fuels = ["Electricity", "Coal", "Wood", "Diesel"]
    if "Category" in df_fuel.columns:
        df_heating = df_fuel[df_fuel["Category"].isin(heating_fuels)]
        if not df_heating.empty and "Year" in df_heating.columns:
            df_heating_agg = (
                df_heating.groupby(["Year", "Category"])["_14_P1_EnergyxFuel"]
                .sum()
                .reset_index()
            )
            fig = px.area(
                df_heating_agg,
                x="Year",
                y="_14_P1_EnergyxFuel",
                color="Category",
                labels={"_14_P1_EnergyxFuel": "Energy (MWh)"},
                color_discrete_sequence=CHART_COLORS,
            )
            st.plotly_chart(fig, width="stretch")

st.caption(
    "💡 Lower gas connections and boiler energy indicate progress in building electrification"
)
