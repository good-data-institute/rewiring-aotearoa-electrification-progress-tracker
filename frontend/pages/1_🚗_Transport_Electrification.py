"""Transport Electrification - Vehicle Fleet Analysis.

This page shows comprehensive vehicle electrification metrics with district/region toggle.
"""

import os
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard_utils import (
    CHART_COLORS,
    add_global_refresh_button,
    add_page_refresh_button,
    aggregate_districts_to_regions,
    calculate_yoy_growth,
    create_paginated_dataframe,
    fetch_dataset,
    filter_annual_aggregates,
)

load_dotenv()

BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
API_BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

st.set_page_config(
    page_title="Transport - Electrification Tracker",
    page_icon="🚗",
    layout="wide",
)

st.title("🚗 Transport Electrification")
st.markdown(
    "**Comprehensive analysis of vehicle fleet electrification across New Zealand**"
)

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Add global refresh button
add_global_refresh_button(API_BASE_URL)

year_range = st.sidebar.slider(
    "Year Range",
    min_value=2010,
    max_value=2025,
    value=(2018, 2025),
    help="Select the time period for analysis",
)

# District vs Region toggle
view_mode = st.sidebar.radio(
    "Geographic Granularity",
    options=["Region View (16 regions)", "District View (67 districts)"],
    index=0,
    help="Choose between aggregated regional view or detailed district view",
)

use_district_view = "District" in view_mode

# Category filter
categories = st.sidebar.multiselect(
    "Vehicle Category",
    options=["Private", "Commercial"],
    default=["Private", "Commercial"],
)

# Sub-category filter
sub_categories = st.sidebar.multiselect(
    "Vehicle Type",
    options=["Light Passenger Vehicle", "Light Commercial Vehicle", "Bus"],
    default=["Light Passenger Vehicle", "Light Commercial Vehicle", "Bus"],
)

include_annual = st.sidebar.checkbox(
    "Include Annual Aggregates",
    value=False,
    help="Include rows with Month='Total'",
)

# Fetch data
with st.spinner("Loading transport data..."):
    datasets = {}

    for dataset_name in [
        "waka_kotahi_ev",
        "waka_kotahi_ff",
        "waka_kotahi_new_ev",
        "waka_kotahi_used_ev",
        "waka_kotahi_fleet_elec",
        "eeca_charging_stations",
    ]:
        try:
            df = fetch_dataset(
                API_BASE_URL,
                dataset_name,
                year_min=year_range[0],
                year_max=year_range[1],
                limit=50000,
            )
            # Filter by categories
            if (
                not df.empty
                and "Category" in df.columns
                and dataset_name != "waka_kotahi_fleet_elec"
                and dataset_name != "eeca_charging_stations"
            ):
                if categories:
                    df = df[df["Category"].isin(categories)]
                if sub_categories and "Sub_Category" in df.columns:
                    df = df[df["Sub_Category"].isin(sub_categories)]

            # Apply annual aggregate filter
            df = filter_annual_aggregates(df, include_annual)

            # Aggregate to regions if needed
            if not use_district_view and "Region" in df.columns:
                df = aggregate_districts_to_regions(df, "Region")
            datasets[dataset_name] = df
        except Exception as e:
            st.sidebar.error(f"Error loading {dataset_name}: {e}")
            datasets[dataset_name] = pd.DataFrame()

st.success(f"✓ Loaded {len([d for d in datasets.values() if not d.empty])} datasets")

# Add page-specific refresh button
TRANSPORT_DATASETS = [
    "waka_kotahi_ev",
    "waka_kotahi_ff",
    "waka_kotahi_new_ev",
    "waka_kotahi_used_ev",
    "waka_kotahi_fleet_elec",
    "eeca_charging_stations",
]
add_page_refresh_button(datasets=TRANSPORT_DATASETS)

# KPIs
st.subheader("Key Transport Metrics")
kpi_cols = st.columns(5)

# KPI 1: Total EVs
with kpi_cols[0]:
    df_ev = datasets.get("waka_kotahi_ev", pd.DataFrame())

    if not df_ev.empty and "_01_P1_EV" in df_ev.columns:
        total_evs = df_ev["_01_P1_EV"].sum()

        # Calculate last 12 months registrations
        if "Year" in df_ev.columns and "Month" in df_ev.columns:
            latest_year = df_ev["Year"].max()
            latest_month = df_ev[df_ev["Year"] == latest_year]["Month"].max()

            last_12_months = df_ev[
                ((df_ev["Year"] == latest_year) & (df_ev["Month"] <= latest_month))
                | ((df_ev["Year"] == latest_year - 1) & (df_ev["Month"] > latest_month))
            ]
            last_12_months_total = last_12_months["_01_P1_EV"].sum()
        else:
            # If only yearly data, use latest year
            last_12_months_total = df_ev["_01_P1_EV"].sum()

        # Total EV Registrations
        st.metric(
            "Total EV Registrations",
            f"{int(total_evs):,}",
            f"{int(last_12_months_total):,} registered in the past 12 months",
            help="Total number of EVs registered during the selected period",
        )
    else:
        st.metric("Total EV Registrations", "N/A")

# KPI 2: Fleet Electrification %
with kpi_cols[1]:
    df_fleet = datasets.get("waka_kotahi_fleet_elec", pd.DataFrame())
    if not df_fleet.empty and "_05_P1_FleetElec" in df_fleet.columns:
        if "Year" in df_fleet.columns:
            latest_year = df_fleet["Year"].max()
            latest_val = df_fleet[df_fleet["Year"] == latest_year][
                "_05_P1_FleetElec"
            ].mean()
            if latest_year > year_range[0]:
                prev_val = df_fleet[df_fleet["Year"] == (latest_year - 1)][
                    "_05_P1_FleetElec"
                ].mean()
                delta = latest_val - prev_val
            else:
                delta = 0
            st.metric(
                "Fleet Electrification",
                f"{latest_val:.2f}%",
                "Overall fleet electrification for selected period",
            )
        else:
            st.metric("Fleet Electrification", "N/A")
    else:
        st.metric("Fleet Electrification", "N/A")

# KPI 3: New EV Sales
with kpi_cols[2]:
    df_new_ev = datasets.get("waka_kotahi_new_ev", pd.DataFrame())

    if not df_new_ev.empty and "_03_P1_NewEV" in df_new_ev.columns:
        total_new_ev = df_new_ev["_03_P1_NewEV"].sum()

        # Calculate last 12 months new EV sales
        if "Year" in df_new_ev.columns and "Month" in df_new_ev.columns:
            latest_year = df_new_ev["Year"].max()
            latest_month = df_new_ev[df_new_ev["Year"] == latest_year]["Month"].max()

            last_12_months = df_new_ev[
                (
                    (df_new_ev["Year"] == latest_year)
                    & (df_new_ev["Month"] <= latest_month)
                )
                | (
                    (df_new_ev["Year"] == latest_year - 1)
                    & (df_new_ev["Month"] > latest_month)
                )
            ]
            last_12_months_total = last_12_months["_03_P1_NewEV"].sum()
        else:
            # If only yearly data, use latest year
            last_12_months_total = df_new_ev["_03_P1_NewEV"].sum()

        st.metric(
            "New EV Sales",
            f"{int(total_new_ev):,}",
            f"{int(last_12_months_total):,} sold in the past 12 months",
            help="Number of new (not used) EVs purchased during the selected period",
        )
    else:
        st.metric("New EV Sales", "N/A")

# KPI 4: Used EV Registrations
with kpi_cols[3]:
    df_used_ev = datasets.get("waka_kotahi_used_ev", pd.DataFrame())

    if not df_used_ev.empty and "_04_P1_UsedEV" in df_used_ev.columns:
        total_used_ev = df_used_ev["_04_P1_UsedEV"].sum()

        # Calculate last 12 months used EV registrations
        if "Year" in df_used_ev.columns and "Month" in df_used_ev.columns:
            latest_year = df_used_ev["Year"].max()
            latest_month = df_used_ev[df_used_ev["Year"] == latest_year]["Month"].max()

            last_12_months = df_used_ev[
                (
                    (df_used_ev["Year"] == latest_year)
                    & (df_used_ev["Month"] <= latest_month)
                )
                | (
                    (df_used_ev["Year"] == latest_year - 1)
                    & (df_used_ev["Month"] > latest_month)
                )
            ]
            last_12_months_total = last_12_months["_04_P1_UsedEV"].sum()
        else:
            # If only yearly data, use latest year
            last_12_months_total = df_used_ev["_04_P1_UsedEV"].sum()

        st.metric(
            "Second-hand EV Sales",
            f"{int(total_used_ev):,}",
            f"{int(last_12_months_total):,} registered in the past 12 months",
            help="Number of used (imported) EVs purchased during the selected period",
        )
    else:
        st.metric("Second-hand EV Sales", "N/A")

# KPI 5: Total Charging Stations
with kpi_cols[4]:
    df_cs = datasets.get("eeca_charging_stations", pd.DataFrame())

    if not df_cs.empty and "_bonus_ChargingStations" in df_cs.columns:
        total_charging_stations = df_cs["_bonus_ChargingStations"].sum()

        # Calculate last 12 months additions
        if "Year" in df_cs.columns and "Month" in df_cs.columns:
            latest_year = df_cs["Year"].max()
            latest_month = df_cs[df_cs["Year"] == latest_year]["Month"].max()

            last_12_months = df_cs[
                ((df_cs["Year"] == latest_year) & (df_cs["Month"] <= latest_month))
                | ((df_cs["Year"] == latest_year - 1) & (df_cs["Month"] > latest_month))
            ]
            last_12_months_total = last_12_months["_bonus_ChargingStations"].sum()
        else:
            last_12_months_total = df_cs["_bonus_ChargingStations"].sum()

        st.metric(
            "EV Charging Stations",
            f"{int(total_charging_stations):,}",
            f"{int(last_12_months_total):,} added in the past 12 months",
            help="Total number of public EV charging stations",
        )
    else:
        st.metric("EV Charging Stations", "N/A")

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

# Chart 1: Fleet Composition Over Time (EVs vs Fossil Fuels)
with col1:
    st.subheader("Fleet Composition: EVs vs Fossil Fuels")

    df_ev = datasets.get("waka_kotahi_ev", pd.DataFrame())
    df_ff = datasets.get("waka_kotahi_ff", pd.DataFrame())

    if not df_ev.empty and not df_ff.empty:
        if "Year" in df_ev.columns and "Year" in df_ff.columns:
            df_ev_agg = df_ev.groupby("Year")["_01_P1_EV"].sum().reset_index()
            df_ev_agg["Type"] = "Electric"
            df_ev_agg.rename(columns={"_01_P1_EV": "Count"}, inplace=True)

            df_ff_agg = df_ff.groupby("Year")["_02_P1_FF"].sum().reset_index()
            df_ff_agg["Type"] = "Fossil Fuel"
            df_ff_agg.rename(columns={"_02_P1_FF": "Count"}, inplace=True)

            df_combined = pd.concat([df_ev_agg, df_ff_agg], ignore_index=True)

            fig = px.area(
                df_combined,
                x="Year",
                y="Count",
                color="Type",
                labels={"Count": "Vehicle Count"},
                color_discrete_map={"Electric": "#2ecc71", "Fossil Fuel": "#e74c3c"},
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient data for fleet composition chart")

# Chart 2: Fleet Electrification % Trend
with col2:
    st.subheader("Fleet Electrification % Over Time")
    df_fleet = datasets.get("waka_kotahi_fleet_elec", pd.DataFrame())
    if not df_fleet.empty and "_05_P1_FleetElec" in df_fleet.columns:
        if (
            "Year" in df_fleet.columns
            and "Region" in df_fleet.columns
            and "Month" in df_fleet.columns
        ):
            # Option A: Year-end snapshot (tail 1 per year/region)
            df_fleet_sorted = df_fleet.sort_values(["Year", "Month"])
            df_fleet_agg = df_fleet_sorted.groupby(["Year", "Region"]).tail(1)

            # Show top regions by most recent electrification %
            latest_year = df_fleet_agg["Year"].max()
            top_regions = df_fleet_agg[df_fleet_agg["Year"] == latest_year].nlargest(
                10, "_05_P1_FleetElec"
            )["Region"]

            df_plot = df_fleet_agg[df_fleet_agg["Region"].isin(top_regions)]

            # Plotly line chart
            fig = px.line(
                df_plot,
                x="Year",
                y="_05_P1_FleetElec",
                color="Region",
                markers=True,
                labels={"_05_P1_FleetElec": "Fleet Electrification %"},
                color_discrete_sequence=CHART_COLORS,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Missing required columns")
    else:
        st.info("No fleet electrification data available")


col3, col4 = st.columns(2)

# Chart 3: New vs Used EV Purchases
with col3:
    st.subheader("New vs Used EV Purchases")

    df_new = datasets.get("waka_kotahi_new_ev", pd.DataFrame())
    df_used = datasets.get("waka_kotahi_used_ev", pd.DataFrame())

    if not df_new.empty and not df_used.empty:
        if "Year" in df_new.columns and "Year" in df_used.columns:
            df_new_agg = df_new.groupby("Year")["_03_P1_NewEV"].sum().reset_index()
            df_used_agg = df_used.groupby("Year")["_04_P1_UsedEV"].sum().reset_index()

            df_combined = df_new_agg.merge(df_used_agg, on="Year", how="outer").fillna(
                0
            )

            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=df_combined["Year"],
                    y=df_combined["_03_P1_NewEV"],
                    name="New EVs",
                    marker_color="#3498db",
                )
            )
            fig.add_trace(
                go.Bar(
                    x=df_combined["Year"],
                    y=df_combined["_04_P1_UsedEV"],
                    name="Used EVs",
                    marker_color="#95a5a6",
                )
            )
            fig.update_layout(
                barmode="group",
                yaxis_title="Vehicle Count",
                xaxis_title="Year",
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient data for new vs used comparison")

# Chart 4: Regional EV Adoption (Top 10)
with col4:
    st.subheader("Top 10 Regions by EV Count")

    df_ev = datasets.get("waka_kotahi_ev", pd.DataFrame())
    if not df_ev.empty and "_01_P1_EV" in df_ev.columns:
        if "Year" in df_ev.columns and "Region" in df_ev.columns:
            latest_year = df_ev["Year"].max()
            df_latest = df_ev[df_ev["Year"] == latest_year]
            df_region = (
                df_latest.groupby("Region")["_01_P1_EV"]
                .sum()
                .nlargest(10)
                .reset_index()
            )

            fig = px.bar(
                df_region,
                y="Region",
                x="_01_P1_EV",
                orientation="h",
                labels={"_01_P1_EV": "Total EVs"},
                color="_01_P1_EV",
                color_continuous_scale="Greens",
            )
            fig.update_layout(showlegend=False, yaxis=dict(autorange="reversed"))

            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No regional EV data available")

# YoY Growth Analysis
st.subheader("Year-over-Year Growth Analysis")

df_ev = datasets.get("waka_kotahi_ev", pd.DataFrame())
if not df_ev.empty and "_01_P1_EV" in df_ev.columns and "Year" in df_ev.columns:
    df_ev_agg = df_ev.groupby("Year")["_01_P1_EV"].sum().reset_index()
    df_ev_agg = calculate_yoy_growth(df_ev_agg, "_01_P1_EV")

    fig = px.bar(
        df_ev_agg,
        x="Year",
        y="_01_P1_EV_yoy",
        labels={"_01_P1_EV_yoy": "YoY Growth %"},
        color="_01_P1_EV_yoy",
        color_continuous_scale="RdYlGn",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Insufficient data for YoY growth analysis")

st.markdown("---")

col5, col6 = st.columns(2)

# Regional analysis of EV charging stations
with col5:
    st.subheader("Top 10 Regions by EV Charging Station Count")

    df_cs = datasets.get("eeca_charging_stations", pd.DataFrame())

    if not df_cs.empty and "_bonus_ChargingStations" in df_cs.columns:
        if "Region" in df_cs.columns:
            # Aggregate total charging stations by region
            df_region = (
                df_cs.groupby("Region")["_bonus_ChargingStations"]
                .sum()
                .nlargest(10)
                .reset_index()
            )

            # Horizontal bar chart
            fig = px.bar(
                df_region,
                y="Region",
                x="_bonus_ChargingStations",
                orientation="h",
                labels={"_bonus_ChargingStations": "Total Charging Stations"},
                color="_bonus_ChargingStations",
                color_continuous_scale="Blues",
            )

            fig.update_layout(showlegend=False, yaxis=dict(autorange="reversed"))

            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No regional charging station data available")

# Charging Stations by kW Range
with col6:
    st.subheader("EV Charging Stations - Count by Power Rating (kW)")

    df_cs_kw = datasets.get("eeca_charging_stations", pd.DataFrame())

    if not df_cs_kw.empty and "Avg_Kw" in df_cs_kw.columns:
        # Define kW ranges and labels
        bins = [0, 10, 25, 75, 175, 500]
        labels = [
            "3-10kW (slow, single-phase)",
            "11-24kW (moderate, multi-phase)",
            "25-74kW (fast, multi-phase)",
            "75-174kW (rapid, multi-phase)",
            "175-475kW (ultra-rapid, multi-phase)",
        ]

        # Bin the Avg_Kw values
        df_cs_kw["Kw_Range"] = pd.cut(
            df_cs_kw["Avg_Kw"], bins=bins, labels=labels, right=False
        )

        # Aggregate: count per kW range
        df_kw_count = df_cs_kw.groupby("Kw_Range").size().reset_index(name="Count")

        # Only show labels if bar height >= threshold
        threshold = df_kw_count["Count"].max() * 0.15  # 10% of max value
        df_kw_count["label"] = df_kw_count["Count"].apply(
            lambda x: str(x) if x >= threshold else ""
        )

        # Create bar chart
        fig = go.Figure(
            go.Bar(
                x=df_kw_count["Kw_Range"],
                y=df_kw_count["Count"],
                text=df_kw_count["label"],  # use conditional labels
                textposition="inside",  # center inside bars
                insidetextanchor="middle",
                marker_color="#020079",
            )
        )

        # Layout
        fig.update_layout(
            yaxis_title="Number of Charging Stations",
            xaxis_title="Power Rating Range",
            title="By Power Rating",
            xaxis_tickangle=-45,
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Insufficient data to display charging stations by kW range")

# Number of Charging Stations per Year
df = datasets.get("eeca_charging_stations", pd.DataFrame())

with st.container():
    st.subheader("EV Charging Stations - Number Operational Over Time")

    if not df.empty and "Year" in df.columns:
        df_year = df.groupby("Year")["_bonus_ChargingStations"].sum().reset_index()

        # Only show labels if bar height >= this value
        threshold = df_year["_bonus_ChargingStations"].max() * 0.1  # 10% of max value

        # Replace small values with empty string for labels
        df_year["label"] = df_year["_bonus_ChargingStations"].apply(
            lambda x: str(x) if x >= threshold else ""
        )

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=df_year["Year"],
                y=df_year["_bonus_ChargingStations"],
                name="Charging Stations",
                marker_color="#110070",
                text=df_year["label"],
                textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="white"),
            )
        )

        fig.update_layout(
            barmode="group",
            xaxis_title="Year",
            yaxis_title="Number of Charging Stations",
        )

        # Ensure x-axis labels always show
        fig.update_xaxes(tickmode="linear", tick0=df_year["Year"].min(), dtick=1)

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No charging station data available")

st.markdown("---")

# Data Table
st.subheader("Detailed Data Explorer")

dataset_choice = st.selectbox(
    "Select Dataset to View",
    options=[
        "EV Count",
        "Fossil Fuel Vehicles",
        "New EV Sales",
        "Used EV Imports",
        "Fleet Electrification %",
        "EV Charging Stations",
    ],
)

dataset_map = {
    "EV Count": "waka_kotahi_ev",
    "Fossil Fuel Vehicles": "waka_kotahi_ff",
    "New EV Sales": "waka_kotahi_new_ev",
    "Used EV Imports": "waka_kotahi_used_ev",
    "Fleet Electrification %": "waka_kotahi_fleet_elec",
    "EV Charging Stations": "eeca_charging_stations",
}

df_display = datasets.get(dataset_map[dataset_choice], pd.DataFrame())

if not df_display.empty:
    st.write(f"**{dataset_choice}** - {len(df_display):,} rows")

    # Pagination
    df_paginated = create_paginated_dataframe(
        df_display, page_size=100, page_key=f"transport_{dataset_choice}"
    )
    st.dataframe(df_paginated, width="stretch")

    # Download
    csv = df_display.to_csv(index=False)
    st.download_button(
        label="📥 Download Full Dataset as CSV",
        data=csv,
        file_name=f"{dataset_map[dataset_choice]}_{year_range[0]}_{year_range[1]}.csv",
        mime="text/csv",
    )
else:
    st.warning("No data available for selected dataset")

st.markdown("---")
st.caption(
    f"💡 Viewing: **{view_mode}** | Use sidebar to toggle between district and region views"
)
