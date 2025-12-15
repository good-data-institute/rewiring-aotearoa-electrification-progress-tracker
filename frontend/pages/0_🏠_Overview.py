"""Overview Dashboard - Holistic Electrification Progress.

This page provides an executive summary view with KPIs across all metrics.
"""

import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard_utils import (
    CHART_COLORS,
    NZ_REGIONS_COORDS,
    add_global_refresh_button,
    add_page_refresh_button,
    fetch_all_datasets,
    filter_annual_aggregates,
    get_latest_kpi_value,
    normalize_to_0_100,
)

# Load environment variables
load_dotenv()

# Configuration
BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
API_BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

# Page configuration
st.set_page_config(
    page_title="Overview - Electrification Tracker",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 Electrification Progress Overview")
st.markdown("**Holistic view of electrification progress across all sectors**")

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Add global refresh button
add_global_refresh_button(API_BASE_URL)

year_range = st.sidebar.slider(
    "Year Range",
    min_value=2015,
    max_value=2025,
    value=(2020, 2025),
    help="Select the time period for analysis",
)

include_annual = st.sidebar.checkbox(
    "Include Annual Aggregates",
    value=False,
    help="Include rows with Month='Total' (annual summaries)",
)

# Fetch data
with st.spinner("Loading data..."):
    datasets = fetch_all_datasets(
        API_BASE_URL,
        year_min=year_range[0],
        year_max=year_range[1],
        load_all=False,
    )

# Apply annual aggregate filter
for dataset_name, df in datasets.items():
    if not df.empty:
        datasets[dataset_name] = filter_annual_aggregates(df, include_annual)

st.success(f"✓ Loaded {len([d for d in datasets.values() if not d.empty])} datasets")

# Add page-specific refresh button
OVERVIEW_DATASETS = [
    "waka_kotahi_fleet_elec",
    "waka_kotahi_ev",
    "waka_kotahi_ff",
    "waka_kotahi_new_ev",
    "waka_kotahi_used_ev",
    "eeca_electricity_percentage",
    "eeca_energy_by_fuel",
    "eeca_boiler_energy",
    "emi_generation_analytics",
    "gic_analytics",
    "battery_penetration_commercial",
    "battery_penetration_residential",
    "solar_penetration",
    "battery_capacity",
]
add_page_refresh_button(datasets=OVERVIEW_DATASETS)

# KPI Cards
st.subheader("Key Performance Indicators")

kpi_cols = st.columns(4)

# KPI 1: Fleet Electrification %
with kpi_cols[0]:
    df_fleet = datasets.get("waka_kotahi_fleet_elec", pd.DataFrame())
    if not df_fleet.empty and "_05_P1_FleetElec" in df_fleet.columns:
        latest, delta = get_latest_kpi_value(df_fleet, "_05_P1_FleetElec")
        st.metric(
            "Fleet Electrification",
            f"{latest:.2f}%",
            f"{delta:+.2f}%",
            help="Percentage of vehicle fleet that is electric",
        )
    else:
        st.metric("Fleet Electrification", "N/A")

# KPI 2: Total EVs on Road
with kpi_cols[1]:
    df_ev = datasets.get("waka_kotahi_ev", pd.DataFrame())
    if not df_ev.empty and "_01_P1_EV" in df_ev.columns:
        # Sum across latest year
        if "Year" in df_ev.columns:
            latest_year = df_ev["Year"].max()
            total_evs = df_ev[df_ev["Year"] == latest_year]["_01_P1_EV"].sum()
            # Get previous year for delta
            if latest_year > year_range[0]:
                prev_evs = df_ev[df_ev["Year"] == (latest_year - 1)]["_01_P1_EV"].sum()
                delta = total_evs - prev_evs
            else:
                delta = 0
            st.metric(
                "Total EVs",
                f"{int(total_evs):,}",
                f"{int(delta):+,}",
                help="Total electric vehicles on road",
            )
        else:
            st.metric("Total EVs", "N/A")
    else:
        st.metric("Total EVs", "N/A")

# KPI 3: Electricity Share
with kpi_cols[2]:
    df_elec = datasets.get("eeca_electricity_percentage", pd.DataFrame())
    if not df_elec.empty and "_13_P1_ElecCons" in df_elec.columns:
        latest, delta = get_latest_kpi_value(df_elec, "_13_P1_ElecCons")
        st.metric(
            "Electricity Share",
            f"{latest:.1f}%",
            f"{delta:+.1f}%",
            help="Electricity's share of total energy consumption",
        )
    else:
        st.metric("Electricity Share", "N/A")

# KPI 4: Renewable Generation
with kpi_cols[3]:
    df_renewable = datasets.get("emi_generation_analytics", pd.DataFrame())
    if not df_renewable.empty and "_12_P1_EnergyRenew" in df_renewable.columns:
        df_renewable["renewable_pct"] = df_renewable["_12_P1_EnergyRenew"] * 100
        latest, delta = get_latest_kpi_value(df_renewable, "renewable_pct")
        st.metric(
            "Renewable Energy",
            f"{latest:.1f}%",
            f"{delta:+.1f}%",
            help="Renewable percentage of electricity generation",
        )
    else:
        st.metric("Renewable Energy", "N/A")

kpi_cols2 = st.columns(4)

# KPI 5: Battery Penetration
with kpi_cols2[0]:
    df_battery = datasets.get("battery_penetration_residential", pd.DataFrame())
    if not df_battery.empty and "_06b_P1_BattPen" in df_battery.columns:
        latest, delta = get_latest_kpi_value(df_battery, "_06b_P1_BattPen")
        st.metric(
            "Battery Penetration",
            f"{latest:.1f}%",
            f"{delta:+.1f}%",
            help="Battery adoption among residential connections",
        )
    else:
        st.metric("Battery Penetration", "N/A")

# KPI 6: Solar Capacity
with kpi_cols2[1]:
    df_solar = datasets.get("solar_penetration", pd.DataFrame())
    if not df_solar.empty and "_07_P1_Sol" in df_solar.columns:
        # Get latest total
        if "Year" in df_solar.columns:
            latest_year = df_solar["Year"].max()
            total_solar = df_solar[df_solar["Year"] == latest_year]["_07_P1_Sol"].sum()
            if latest_year > year_range[0]:
                prev_solar = df_solar[df_solar["Year"] == (latest_year - 1)][
                    "_07_P1_Sol"
                ].sum()
                delta = total_solar - prev_solar
            else:
                delta = 0
            st.metric(
                "Solar Capacity",
                f"{total_solar:.1f} MW",
                f"{delta:+.1f} MW",
                help="Total solar capacity installed",
            )
        else:
            st.metric("Solar Capacity", "N/A")
    else:
        st.metric("Solar Capacity", "N/A")

# KPI 7: Gas Connections
with kpi_cols2[2]:
    df_gas = datasets.get("gic_analytics", pd.DataFrame())
    if not df_gas.empty and "_10_P1_Gas" in df_gas.columns:
        latest, delta = get_latest_kpi_value(df_gas, "_10_P1_Gas")
        st.metric(
            "New Gas Connections",
            f"{int(latest)}",
            f"{int(delta):+d}",
            delta_color="inverse",
            help="Lower is better for electrification progress",
        )
    else:
        st.metric("New Gas Connections", "N/A")

# KPI 8: Boiler Energy (Fossil Fuels)
with kpi_cols2[3]:
    df_boiler = datasets.get("eeca_boiler_energy", pd.DataFrame())
    if not df_boiler.empty and "_11_P1_EnergyFF" in df_boiler.columns:
        latest, delta = get_latest_kpi_value(df_boiler, "_11_P1_EnergyFF")
        st.metric(
            "Fossil Boiler Energy",
            f"{latest / 1000:.1f} GWh",
            f"{delta / 1000:+.1f} GWh",
            delta_color="inverse",
            help="Lower is better - fossil fuel energy for boilers",
        )
    else:
        st.metric("Fossil Boiler Energy", "N/A")

st.markdown("---")

# Charts
st.subheader("Progress Indicators")

col1, col2 = st.columns(2)

# Chart 1: Normalized Multi-Metric Timeline
with col1:
    st.markdown("**Normalized Progress Comparison (0-100 Scale)**")

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
            df_norm["metric"] = "Fleet Electrification %"
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
            df_norm["metric"] = "Electricity Share %"
            normalized_data.append(df_norm[["Year", "value", "metric"]])

    # Renewable generation
    df_renewable = datasets.get("emi_generation_analytics", pd.DataFrame())
    if (
        not df_renewable.empty
        and "_12_P1_EnergyRenew" in df_renewable.columns
        and "Year" in df_renewable.columns
    ):
        df_norm = (
            df_renewable.groupby("Year")["_12_P1_EnergyRenew"].mean().reset_index()
        )
        if len(df_norm) > 1:
            df_norm["value"] = normalize_to_0_100(df_norm["_12_P1_EnergyRenew"])
            df_norm["metric"] = "Renewable Generation %"
            normalized_data.append(df_norm[["Year", "value", "metric"]])

    # Battery penetration
    df_battery = datasets.get("battery_penetration_residential", pd.DataFrame())
    if (
        not df_battery.empty
        and "_06b_P1_BattPen" in df_battery.columns
        and "Year" in df_battery.columns
    ):
        df_norm = df_battery.groupby("Year")["_06b_P1_BattPen"].mean().reset_index()
        if len(df_norm) > 1:
            df_norm["value"] = normalize_to_0_100(df_norm["_06b_P1_BattPen"])
            df_norm["metric"] = "Battery Penetration %"
            normalized_data.append(df_norm[["Year", "value", "metric"]])

    # Gas connections (inverted)
    df_gas = datasets.get("gic_analytics", pd.DataFrame())
    if not df_gas.empty and "_10_P1_Gas" in df_gas.columns and "Year" in df_gas.columns:
        df_norm = df_gas.groupby("Year")["_10_P1_Gas"].sum().reset_index()
        if len(df_norm) > 1:
            df_norm["value"] = 100 - normalize_to_0_100(df_norm["_10_P1_Gas"])
            df_norm["metric"] = "Gas Decline (inverted)"
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
        fig.update_layout(height=400)
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Insufficient data for normalized comparison")

# Chart 2: Regional Progress Map
with col2:
    st.markdown("**Regional Electrification Progress**")

    # Calculate composite score for each region
    regional_scores = {}

    # Fleet electrification contribution
    df_fleet = datasets.get("waka_kotahi_fleet_elec", pd.DataFrame())
    if (
        not df_fleet.empty
        and "Region" in df_fleet.columns
        and "_05_P1_FleetElec" in df_fleet.columns
    ):
        fleet_by_region = df_fleet.groupby("Region")["_05_P1_FleetElec"].mean()
        for region, value in fleet_by_region.items():
            regional_scores[region] = (
                regional_scores.get(region, 0) + value * 25
            )  # 25% weight

    # Renewable generation contribution
    df_renewable = datasets.get("emi_generation_analytics", pd.DataFrame())
    if (
        not df_renewable.empty
        and "Region" in df_renewable.columns
        and "_12_P1_EnergyRenew" in df_renewable.columns
    ):
        renewable_by_region = df_renewable.groupby("Region")[
            "_12_P1_EnergyRenew"
        ].mean()
        for region, value in renewable_by_region.items():
            regional_scores[region] = (
                regional_scores.get(region, 0) + value * 25 * 100
            )  # 25% weight, convert to %

    # Battery penetration contribution
    df_battery = datasets.get("battery_penetration_residential", pd.DataFrame())
    if (
        not df_battery.empty
        and "Region" in df_battery.columns
        and "_06b_P1_BattPen" in df_battery.columns
    ):
        battery_by_region = df_battery.groupby("Region")["_06b_P1_BattPen"].mean()
        for region, value in battery_by_region.items():
            regional_scores[region] = (
                regional_scores.get(region, 0) + value * 25
            )  # 25% weight

    # Gas connections contribution (inverted - lower is better)
    df_gas = datasets.get("gic_analytics", pd.DataFrame())
    if (
        not df_gas.empty
        and "Region" in df_gas.columns
        and "_10_P1_Gas" in df_gas.columns
    ):
        gas_by_region = df_gas.groupby("Region")["_10_P1_Gas"].sum()
        if len(gas_by_region) > 0:
            gas_normalized = 100 - (
                100
                * (gas_by_region - gas_by_region.min())
                / (gas_by_region.max() - gas_by_region.min())
            )
            for region, value in gas_normalized.items():
                regional_scores[region] = (
                    regional_scores.get(region, 0) + value * 25
                )  # 25% weight

    if regional_scores:
        df_scores = pd.DataFrame(
            list(regional_scores.items()), columns=["Region", "Progress_Score"]
        )
        df_scores["lat"] = df_scores["Region"].map(
            lambda r: NZ_REGIONS_COORDS.get(r, {}).get("lat")
        )
        df_scores["lon"] = df_scores["Region"].map(
            lambda r: NZ_REGIONS_COORDS.get(r, {}).get("lon")
        )
        df_scores = df_scores.dropna(subset=["lat", "lon"])

        fig = go.Figure(
            data=go.Scattergeo(
                lon=df_scores["lon"],
                lat=df_scores["lat"],
                text=df_scores["Region"],
                mode="markers",
                marker=dict(
                    size=df_scores["Progress_Score"] / 3,
                    color=df_scores["Progress_Score"],
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(title="Score"),
                    line=dict(width=1, color="white"),
                ),
                hovertemplate="<b>%{text}</b><br>Progress Score: %{marker.color:.1f}<extra></extra>",
            )
        )

        fig.update_geos(
            center=dict(lon=173, lat=-41),
            projection_scale=15,
            showcountries=True,
            showland=True,
            landcolor="rgb(243, 243, 243)",
            coastlinecolor="rgb(204, 204, 204)",
        )
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Insufficient data for regional map")

st.markdown("---")

# Bottom section
col3, col4 = st.columns(2)

# Chart 3: EV Growth
with col3:
    st.markdown("**Electric Vehicle Growth**")
    df_ev = datasets.get("waka_kotahi_ev", pd.DataFrame())
    if not df_ev.empty and "_01_P1_EV" in df_ev.columns and "Year" in df_ev.columns:
        df_ev_agg = df_ev.groupby("Year")["_01_P1_EV"].sum().reset_index()
        fig = px.area(
            df_ev_agg,
            x="Year",
            y="_01_P1_EV",
            labels={"_01_P1_EV": "Total EVs"},
            color_discrete_sequence=["#2ecc71"],
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No EV data available")

# Chart 4: Energy Mix Evolution
with col4:
    st.markdown("**Energy Consumption by Fuel Type**")
    df_fuel = datasets.get("eeca_energy_by_fuel", pd.DataFrame())
    if (
        not df_fuel.empty
        and "_14_P1_EnergyxFuel" in df_fuel.columns
        and "Year" in df_fuel.columns
        and "Category" in df_fuel.columns
    ):
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
        fig.update_layout(height=300)
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No fuel mix data available")

st.markdown("---")
st.caption(
    "💡 Navigate to specific pages using the sidebar for detailed analysis of each metric category."
)
