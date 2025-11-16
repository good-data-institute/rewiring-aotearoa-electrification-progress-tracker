"""Streamlit dashboard for Electrification Progress data.

Enhanced dashboard with interactive filters, visualizations, and
holistic analysis across all metrics datasets.
"""

import os
import warnings

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from dotenv import load_dotenv

from dashboard_utils import (
    CHART_COLORS,
    NZ_REGIONS_COORDS,
    fetch_all_datasets,
    filter_annual_aggregates,
    get_latest_kpi_value,
    normalize_to_0_100,
)

# Suppress warnings
warnings.filterwarnings("ignore")
st.set_option("deprecation.showPyplotGlobalUse", False)

# Load environment variables
load_dotenv()

# Configuration
BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
API_BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

# Page configuration
st.set_page_config(
    page_title="Electrification Progress Tracker",
    page_icon="⚡",
    layout="wide",
)

# Initialize session state
if "selected_region" not in st.session_state:
    st.session_state.selected_region = None


def check_backend_health():
    """Check if backend API is available."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


# Check backend status
if not check_backend_health():
    st.error(
        f"⚠️ Backend API is not available at {API_BASE_URL}. "
        "Please ensure the backend is running."
    )
    st.info("To start the backend, run: `python -m backend.main`")
    st.stop()

# Title and description
st.title("⚡ Rewiring Aotearoa Electrification Progress Tracker")
st.markdown(
    "Interactive dashboard for holistic electrification progress analysis across New Zealand"
)

# ===== SIDEBAR FILTERS =====
st.sidebar.header("🔍 Filters")

# Year range filter
year_range = st.sidebar.slider(
    "Year Range",
    min_value=2013,
    max_value=2025,
    value=(2020, 2025),
    help="Select the time period for analysis",
)

# Region filter
all_regions = ["All"] + sorted([r for r in NZ_REGIONS_COORDS.keys()])
selected_regions = st.sidebar.multiselect(
    "Regions",
    options=all_regions,
    default=["All"],
    help="Select one or more regions to analyze",
)

# Sector filter
all_sectors = ["All", "Commercial", "Industrial", "Residential", "SME", "Transport"]
selected_sectors = st.sidebar.multiselect(
    "Sectors",
    options=all_sectors,
    default=["All"],
    help="Filter by sector/sub-category",
)

# Annual aggregates checkbox
st.sidebar.markdown("**📅 Data Granularity**")
st.sidebar.caption(
    "Some datasets include annual summaries (Month='Total') alongside monthly data. "
    "Uncheck to show only monthly records for time series analysis."
)
include_annual = st.sidebar.checkbox(
    "Include Annual Aggregates",
    value=False,
    help="Include rows with Month='Total' (annual summaries)",
)

# Load all data checkbox
load_all_data = st.sidebar.checkbox(
    "Load All Data", value=False, help="Load all data without pagination (may be slow)"
)

# Clear region filter button
if st.session_state.selected_region:
    st.sidebar.info(f"🎯 Filtered to: {st.session_state.selected_region}")
    if st.sidebar.button("Clear Region Filter"):
        st.session_state.selected_region = None
        st.rerun()

# Refresh button
if st.sidebar.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("*Data sources: EMI, EECA, GIC*")

# ===== FETCH DATA =====
with st.spinner("Loading data from backend..."):
    # Apply session state region filter if set
    regions_to_fetch = selected_regions
    if st.session_state.selected_region and st.session_state.selected_region != "All":
        regions_to_fetch = [st.session_state.selected_region]

    datasets = fetch_all_datasets(
        API_BASE_URL,
        year_min=year_range[0],
        year_max=year_range[1],
        regions=regions_to_fetch if regions_to_fetch != ["All"] else None,
        sectors=selected_sectors if selected_sectors != ["All"] else None,
        load_all=load_all_data,
    )

# Apply annual aggregate filter
for dataset_name, df in datasets.items():
    if not df.empty:
        datasets[dataset_name] = filter_annual_aggregates(df, include_annual)

st.success(f"✓ Loaded {len([d for d in datasets.values() if not d.empty])} datasets")

# ===== TABS FOR DIFFERENT VIEWS =====
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📊 Overview Dashboard",
        "🗺️ Regional Analysis",
        "🏭 Sector Deep-Dive",
        "📈 Time Series & Correlation",
        "💾 Data Export",
    ]
)

# ===== TAB 1: OVERVIEW DASHBOARD =====
with tab1:
    st.header("Overview Dashboard")
    st.markdown("Key performance indicators and trend visualizations")

    # KPI Cards
    st.subheader("Key Metrics")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    # KPI 1: Electricity Percentage
    with kpi_col1:
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

    # KPI 2: Renewable Generation
    with kpi_col2:
        df_renewable = datasets.get("emi_generation_analytics", pd.DataFrame())
        if not df_renewable.empty and "_12_P1_EnergyRenew" in df_renewable.columns:
            # Convert to percentage
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

    # KPI 3: Battery Penetration
    with kpi_col3:
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

    # KPI 4: Gas Connections (inverse indicator)
    with kpi_col4:
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

    st.markdown("---")

    # Charts Grid
    chart_col1, chart_col2 = st.columns(2)

    # Chart 1: Electricity Percentage Trend
    with chart_col1:
        st.subheader("Electricity Share Trend")
        df_elec = datasets.get("eeca_electricity_percentage", pd.DataFrame())
        df_elec.to_csv("debug_elec.csv")
        if not df_elec.empty and "_13_P1_ElecCons" in df_elec.columns:
            fig = px.line(
                df_elec,
                x="Year",
                y="_13_P1_ElecCons",
                title="Electricity Share of Total Energy Consumption",
                labels={"_13_P1_ElecCons": "Electricity %"},
                markers=True,
                color_discrete_sequence=CHART_COLORS,
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No data available for electricity percentage")

    # Chart 2: Renewable Generation Box Plot
    with chart_col2:
        st.subheader("Renewable Energy by Region")
        df_renewable = datasets.get("emi_generation_analytics", pd.DataFrame())
        if not df_renewable.empty and "_12_P1_EnergyRenew" in df_renewable.columns:
            df_renewable["renewable_pct"] = df_renewable["_12_P1_EnergyRenew"] * 100
            if "Region" in df_renewable.columns:
                fig = px.box(
                    df_renewable,
                    x="Region",
                    y="renewable_pct",
                    title="Renewable Energy Distribution by Region",
                    labels={"renewable_pct": "Renewable %"},
                    color_discrete_sequence=CHART_COLORS,
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("No regional data available")
        else:
            st.info("No data available for renewable generation")

    chart_col3, chart_col4 = st.columns(2)

    # Chart 3: Energy by Fuel Stacked Area
    with chart_col3:
        st.subheader("Energy Consumption by Fuel Type")
        df_fuel = datasets.get("eeca_energy_by_fuel", pd.DataFrame())
        if not df_fuel.empty and "_14_P1_EnergyxFuel" in df_fuel.columns:
            if "Category" in df_fuel.columns and "Year" in df_fuel.columns:
                # Aggregate by year and fuel category
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
                    title="Energy Consumption by Fuel Type Over Time",
                    labels={"_14_P1_EnergyxFuel": "Energy (GWh)"},
                    color_discrete_sequence=CHART_COLORS,
                )
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("Missing required columns for fuel analysis")
        else:
            st.info("No data available for energy by fuel")

    # Chart 4: Gas Connections Decline
    with chart_col4:
        st.subheader("Gas Connections Trend")
        df_gas = datasets.get("gic_analytics", pd.DataFrame())
        if not df_gas.empty and "_10_P1_Gas" in df_gas.columns:
            if "Year" in df_gas.columns:
                # Aggregate by year
                df_gas_agg = df_gas.groupby("Year")["_10_P1_Gas"].sum().reset_index()
                fig = px.line(
                    df_gas_agg,
                    x="Year",
                    y="_10_P1_Gas",
                    title="New Gas Connections (Declining = Good)",
                    labels={"_10_P1_Gas": "New Connections"},
                    markers=True,
                    color_discrete_sequence=["#FF6B6B"],  # Red for gas
                )
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("Missing Year column")
        else:
            st.info("No data available for gas connections")

# ===== TAB 2: REGIONAL ANALYSIS =====
with tab2:
    st.header("Regional Analysis")
    st.markdown("Interactive map and regional comparisons across New Zealand")

    # Scattergeo Map
    st.subheader("Interactive Regional Map")

    map_metric = st.radio(
        "Select Metric to Display",
        options=["Renewable Energy %", "Gas Connections", "Battery Penetration"],
        horizontal=True,
    )

    # Prepare map data based on selected metric
    if map_metric == "Renewable Energy %":
        df_map = datasets.get("emi_generation_analytics", pd.DataFrame())
        if (
            not df_map.empty
            and "Region" in df_map.columns
            and "_12_P1_EnergyRenew" in df_map.columns
        ):
            # Aggregate by region (average)
            df_map_agg = (
                df_map.groupby("Region")["_12_P1_EnergyRenew"].mean().reset_index()
            )
            df_map_agg["value"] = df_map_agg["_12_P1_EnergyRenew"] * 100

            # Add coordinates
            df_map_agg["lat"] = df_map_agg["Region"].map(
                lambda r: NZ_REGIONS_COORDS.get(r, {}).get("lat")
            )
            df_map_agg["lon"] = df_map_agg["Region"].map(
                lambda r: NZ_REGIONS_COORDS.get(r, {}).get("lon")
            )
            df_map_agg = df_map_agg.dropna(subset=["lat", "lon"])

            # Create scattergeo
            fig = go.Figure(
                data=go.Scattergeo(
                    lon=df_map_agg["lon"],
                    lat=df_map_agg["lat"],
                    text=df_map_agg["Region"],
                    mode="markers",
                    marker=dict(
                        size=df_map_agg["value"] / 2,
                        color=df_map_agg["value"],
                        colorscale="Greens",
                        showscale=True,
                        colorbar=dict(title="Renewable %"),
                        line=dict(width=1, color="white"),
                    ),
                    hovertemplate="<b>%{text}</b><br>Renewable: %{marker.color:.1f}%<extra></extra>",
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

            fig.update_layout(title="Renewable Energy % by Region")
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No renewable generation data available for mapping")

    elif map_metric == "Gas Connections":
        df_map = datasets.get("gic_analytics", pd.DataFrame())
        if (
            not df_map.empty
            and "Region" in df_map.columns
            and "_10_P1_Gas" in df_map.columns
        ):
            # Aggregate by region (sum)
            df_map_agg = df_map.groupby("Region")["_10_P1_Gas"].sum().reset_index()
            df_map_agg["value"] = df_map_agg["_10_P1_Gas"]

            # Add coordinates
            df_map_agg["lat"] = df_map_agg["Region"].map(
                lambda r: NZ_REGIONS_COORDS.get(r, {}).get("lat")
            )
            df_map_agg["lon"] = df_map_agg["Region"].map(
                lambda r: NZ_REGIONS_COORDS.get(r, {}).get("lon")
            )
            df_map_agg = df_map_agg.dropna(subset=["lat", "lon"])

            # Create scattergeo
            fig = go.Figure(
                data=go.Scattergeo(
                    lon=df_map_agg["lon"],
                    lat=df_map_agg["lat"],
                    text=df_map_agg["Region"],
                    mode="markers",
                    marker=dict(
                        size=df_map_agg["value"] / 10,
                        color=df_map_agg["value"],
                        colorscale="Reds",
                        showscale=True,
                        colorbar=dict(title="Connections"),
                        line=dict(width=1, color="white"),
                    ),
                    hovertemplate="<b>%{text}</b><br>Connections: %{marker.color:.0f}<extra></extra>",
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

            fig.update_layout(title="Gas Connections by Region (Lower = Better)")
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No gas connections data available for mapping")

    else:  # Battery Penetration
        df_map = datasets.get("battery_penetration_residential", pd.DataFrame())
        if (
            not df_map.empty
            and "Region" in df_map.columns
            and "_06b_P1_BattPen" in df_map.columns
        ):
            # Aggregate by region (average)
            df_map_agg = (
                df_map.groupby("Region")["_06b_P1_BattPen"].mean().reset_index()
            )
            df_map_agg["value"] = df_map_agg["_06b_P1_BattPen"]

            # Add coordinates
            df_map_agg["lat"] = df_map_agg["Region"].map(
                lambda r: NZ_REGIONS_COORDS.get(r, {}).get("lat")
            )
            df_map_agg["lon"] = df_map_agg["Region"].map(
                lambda r: NZ_REGIONS_COORDS.get(r, {}).get("lon")
            )
            df_map_agg = df_map_agg.dropna(subset=["lat", "lon"])

            # Create scattergeo
            fig = go.Figure(
                data=go.Scattergeo(
                    lon=df_map_agg["lon"],
                    lat=df_map_agg["lat"],
                    text=df_map_agg["Region"],
                    mode="markers",
                    marker=dict(
                        size=df_map_agg["value"] / 2,
                        color=df_map_agg["value"],
                        colorscale="Blues",
                        showscale=True,
                        colorbar=dict(title="Battery %"),
                        line=dict(width=1, color="white"),
                    ),
                    hovertemplate="<b>%{text}</b><br>Battery: %{marker.color:.1f}%<extra></extra>",
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

            fig.update_layout(title="Battery Penetration by Region")
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No battery penetration data available for mapping")

    st.markdown("---")

    # Regional Heatmap
    st.subheader("Regional Performance Matrix")

    # Collect regional metrics
    regional_metrics = []

    # Renewable energy
    df_renewable = datasets.get("emi_generation_analytics", pd.DataFrame())
    if not df_renewable.empty and "Region" in df_renewable.columns:
        df_ren_agg = (
            df_renewable.groupby("Region")["_12_P1_EnergyRenew"].mean().reset_index()
        )
        df_ren_agg.columns = ["Region", "Renewable %"]
        df_ren_agg["Renewable %"] *= 100
        regional_metrics.append(df_ren_agg)

    # Gas connections
    df_gas = datasets.get("gic_analytics", pd.DataFrame())
    if not df_gas.empty and "Region" in df_gas.columns:
        df_gas_agg = df_gas.groupby("Region")["_10_P1_Gas"].sum().reset_index()
        df_gas_agg.columns = ["Region", "Gas Connections"]
        regional_metrics.append(df_gas_agg)

    # Battery penetration
    df_battery = datasets.get("battery_penetration_residential", pd.DataFrame())
    if not df_battery.empty and "Region" in df_battery.columns:
        df_batt_agg = (
            df_battery.groupby("Region")["_06b_P1_BattPen"].mean().reset_index()
        )
        df_batt_agg.columns = ["Region", "Battery %"]
        regional_metrics.append(df_batt_agg)

    if regional_metrics:
        # Merge all metrics
        df_regional = regional_metrics[0]
        for df in regional_metrics[1:]:
            df_regional = df_regional.merge(df, on="Region", how="outer")

        # Display as table
        st.dataframe(df_regional, width="stretch")
    else:
        st.info("No regional metrics available")

# ===== TAB 3: SECTOR DEEP-DIVE =====
with tab3:
    st.header("Sector Deep-Dive")
    st.markdown("Detailed analysis by sector and fuel type")

    # Waterfall Chart for Energy by Fuel
    st.subheader("Energy Consumption Changes by Fuel Type")

    waterfall_view = st.radio(
        "Select View",
        options=[
            "Summary View: Fossil/Renewable/Electricity",
            "Detailed View: All Fuels × Sectors",
        ],
        index=0,
    )

    df_fuel = datasets.get("eeca_energy_by_fuel", pd.DataFrame())
    if not df_fuel.empty and "_14_P1_EnergyxFuel" in df_fuel.columns:
        if "Year" in df_fuel.columns and "Category" in df_fuel.columns:
            # Get first and last year in filtered data
            years = sorted(df_fuel["Year"].unique())
            if len(years) >= 2:
                first_year = years[0]
                last_year = years[-1]

                if waterfall_view.startswith("Summary"):
                    # Summary view: Fossil vs Renewable vs Electricity
                    fossil_fuels = ["Coal", "Diesel", "Petrol"]
                    renewable_fuels = ["Wood", "Other"]

                    df_fuel["Fuel_Type"] = df_fuel["Category"].apply(
                        lambda x: "Electricity"
                        if x == "Electricity"
                        else "Fossil Fuels"
                        if x in fossil_fuels
                        else "Renewable Fuels"
                        if x in renewable_fuels
                        else "Other"
                    )

                    # Calculate totals for each year
                    df_first = (
                        df_fuel[df_fuel["Year"] == first_year]
                        .groupby("Fuel_Type")["_14_P1_EnergyxFuel"]
                        .sum()
                    )
                    df_last = (
                        df_fuel[df_fuel["Year"] == last_year]
                        .groupby("Fuel_Type")["_14_P1_EnergyxFuel"]
                        .sum()
                    )

                    changes = (df_last - df_first).to_dict()

                    # Create waterfall chart
                    categories = list(changes.keys())
                    values = list(changes.values())

                    fig = go.Figure(
                        go.Waterfall(
                            x=categories,
                            y=values,
                            text=[f"{v:+.0f}" for v in values],
                            textposition="outside",
                            connector={"line": {"color": "rgb(63, 63, 63)"}},
                        )
                    )

                    fig.update_layout(
                        title=f"Energy Consumption Changes: {first_year} to {last_year}",
                        yaxis_title="Change in Energy (GWh)",
                        showlegend=False,
                    )

                    st.plotly_chart(fig, width="stretch")

                else:
                    # Detailed view: All fuels × sectors
                    df_first = (
                        df_fuel[df_fuel["Year"] == first_year]
                        .groupby(["Category", "Sub-Category"])["_14_P1_EnergyxFuel"]
                        .sum()
                    )
                    df_last = (
                        df_fuel[df_fuel["Year"] == last_year]
                        .groupby(["Category", "Sub-Category"])["_14_P1_EnergyxFuel"]
                        .sum()
                    )

                    changes = (df_last - df_first).reset_index()
                    changes.columns = ["Category", "Sub-Category", "Change"]
                    changes["Label"] = (
                        changes["Category"] + " - " + changes["Sub-Category"]
                    )

                    # Sort by change magnitude
                    changes = changes.sort_values("Change", ascending=False)

                    fig = go.Figure(
                        go.Waterfall(
                            x=changes["Label"],
                            y=changes["Change"],
                            text=[f"{v:+.0f}" for v in changes["Change"]],
                            textposition="outside",
                            connector={"line": {"color": "rgb(63, 63, 63)"}},
                        )
                    )

                    fig.update_layout(
                        title=f"Detailed Energy Changes: {first_year} to {last_year}",
                        yaxis_title="Change in Energy (GWh)",
                        showlegend=False,
                        xaxis_tickangle=-45,
                    )

                    st.plotly_chart(fig, width="stretch")
            else:
                st.info("Need at least 2 years of data for waterfall chart")
        else:
            st.info("Missing required columns for fuel analysis")
    else:
        st.info("No energy by fuel data available")

    st.markdown("---")

    # Solar/Battery Adoption by Sector
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Solar Adoption by Sector")
        df_solar = datasets.get("solar_penetration", pd.DataFrame())
        if not df_solar.empty and "_07_P1_Sol" in df_solar.columns:
            if "Year" in df_solar.columns and "Sub-Category" in df_solar.columns:
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
                    title="Solar Penetration Trends by Sector",
                    labels={"_07_P1_Sol": "Solar Penetration"},
                    markers=True,
                    color_discrete_sequence=CHART_COLORS,
                )
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("Missing required columns")
        else:
            st.info("No solar penetration data available")

    with col2:
        st.subheader("Battery Adoption by Sector")
        df_battery_com = datasets.get("battery_penetration_commercial", pd.DataFrame())
        df_battery_res = datasets.get("battery_penetration_residential", pd.DataFrame())

        if not df_battery_res.empty and "_06b_P1_BattPen" in df_battery_res.columns:
            if (
                "Year" in df_battery_res.columns
                and "Sub-Category" in df_battery_res.columns
            ):
                df_batt_agg = (
                    df_battery_res.groupby(["Year", "Sub-Category"])["_06b_P1_BattPen"]
                    .mean()
                    .reset_index()
                )
                fig = px.line(
                    df_batt_agg,
                    x="Year",
                    y="_06b_P1_BattPen",
                    color="Sub-Category",
                    title="Battery Penetration Trends by Sector",
                    labels={"_06b_P1_BattPen": "Battery %"},
                    markers=True,
                    color_discrete_sequence=CHART_COLORS,
                )
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("Missing required columns")
        else:
            st.info("No battery penetration data available")

# ===== TAB 4: TIME SERIES & CORRELATION =====
with tab4:
    st.header("Time Series & Correlation Analysis")
    st.markdown("Normalized trends and metric relationships")

    # Normalized Multi-Line Chart
    st.subheader("Normalized Metric Comparison (0-100 Scale)")

    # Prepare normalized data
    normalized_data = []

    # Electricity percentage
    df_elec = datasets.get("eeca_electricity_percentage", pd.DataFrame())
    if (
        not df_elec.empty
        and "_13_P1_ElecCons" in df_elec.columns
        and "Year" in df_elec.columns
    ):
        df_norm = df_elec.groupby("Year")["_13_P1_ElecCons"].mean().reset_index()
        df_norm["value"] = normalize_to_0_100(df_norm["_13_P1_ElecCons"])
        df_norm["metric"] = "Electricity %"
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
        df_norm["value"] = normalize_to_0_100(df_norm["_12_P1_EnergyRenew"])
        df_norm["metric"] = "Renewable %"
        normalized_data.append(df_norm[["Year", "value", "metric"]])

    # Battery penetration
    df_battery = datasets.get("battery_penetration_residential", pd.DataFrame())
    if (
        not df_battery.empty
        and "_06b_P1_BattPen" in df_battery.columns
        and "Year" in df_battery.columns
    ):
        df_norm = df_battery.groupby("Year")["_06b_P1_BattPen"].mean().reset_index()
        df_norm["value"] = normalize_to_0_100(df_norm["_06b_P1_BattPen"])
        df_norm["metric"] = "Battery %"
        normalized_data.append(df_norm[["Year", "value", "metric"]])

    # Gas connections (inverted)
    df_gas = datasets.get("gic_analytics", pd.DataFrame())
    if not df_gas.empty and "_10_P1_Gas" in df_gas.columns and "Year" in df_gas.columns:
        df_norm = df_gas.groupby("Year")["_10_P1_Gas"].sum().reset_index()
        # Invert for comparison (lower gas = better)
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
            title="Normalized Electrification Progress Indicators",
            labels={"value": "Normalized Value (0-100)"},
            markers=True,
            color_discrete_sequence=CHART_COLORS,
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("No data available for normalized comparison")

    st.markdown("---")

    # Correlation Matrix
    st.subheader("Metric Correlation Matrix")

    # Prepare correlation data
    corr_data = {}

    df_elec = datasets.get("eeca_electricity_percentage", pd.DataFrame())
    if (
        not df_elec.empty
        and "_13_P1_ElecCons" in df_elec.columns
        and "Year" in df_elec.columns
    ):
        corr_data["Electricity %"] = df_elec.groupby("Year")["_13_P1_ElecCons"].mean()

    df_renewable = datasets.get("emi_generation_analytics", pd.DataFrame())
    if (
        not df_renewable.empty
        and "_12_P1_EnergyRenew" in df_renewable.columns
        and "Year" in df_renewable.columns
    ):
        corr_data["Renewable %"] = (
            df_renewable.groupby("Year")["_12_P1_EnergyRenew"].mean() * 100
        )

    df_battery = datasets.get("battery_penetration_residential", pd.DataFrame())
    if (
        not df_battery.empty
        and "_06b_P1_BattPen" in df_battery.columns
        and "Year" in df_battery.columns
    ):
        corr_data["Battery %"] = df_battery.groupby("Year")["_06b_P1_BattPen"].mean()

    df_gas = datasets.get("gic_analytics", pd.DataFrame())
    if not df_gas.empty and "_10_P1_Gas" in df_gas.columns and "Year" in df_gas.columns:
        corr_data["Gas Connections"] = df_gas.groupby("Year")["_10_P1_Gas"].sum()

    if len(corr_data) >= 2:
        df_corr = pd.DataFrame(corr_data)
        corr_matrix = df_corr.corr()

        fig = px.imshow(
            corr_matrix,
            text_auto=".2f",
            title="Correlation Between Electrification Metrics",
            color_continuous_scale="RdBu_r",
            aspect="auto",
            zmin=-1,
            zmax=1,
        )
        st.plotly_chart(fig, width="stretch")

        st.info(
            "💡 **Interpretation**: Positive correlation (blue) means metrics move together. "
            "Negative correlation (red) means metrics move in opposite directions. "
            "For example, we expect battery adoption to be negatively correlated with gas connections."
        )
    else:
        st.info(
            "Need at least 2 metrics with overlapping years for correlation analysis"
        )

# ===== TAB 5: DATA EXPORT =====
with tab5:
    st.header("Data Export")
    st.markdown("Download filtered datasets for further analysis")

    export_dataset = st.selectbox(
        "Select Dataset to Export", options=list(datasets.keys())
    )

    df_export = datasets.get(export_dataset, pd.DataFrame())
    if not df_export.empty:
        st.write(f"Dataset: **{export_dataset}** - {len(df_export)} rows")

        # Preview the data
        st.subheader("Data Preview")
        st.dataframe(df_export.head(10), width="stretch")

        # Download button
        csv = df_export.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"{export_dataset}_{year_range[0]}_{year_range[1]}.csv",
            mime="text/csv",
        )

        # Show basic statistics
        st.subheader("Dataset Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", len(df_export))
        with col2:
            st.metric("Total Columns", len(df_export.columns))
        with col3:
            if "Year" in df_export.columns:
                years = df_export["Year"].unique()
                st.metric("Year Range", f"{min(years)}-{max(years)}")
            else:
                st.metric("Year Range", "N/A")
    else:
        st.warning("No data available for selected dataset")
