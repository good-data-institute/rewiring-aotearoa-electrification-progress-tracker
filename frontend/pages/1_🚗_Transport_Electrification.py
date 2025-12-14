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
    default=["Light Passenger Vehicle"],
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
            if not df.empty and "Category" in df.columns:
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
]
add_page_refresh_button(datasets=TRANSPORT_DATASETS)

# KPIs
st.subheader("Key Transport Metrics")
kpi_cols = st.columns(4)

# KPI 1: Total EVs
with kpi_cols[0]:
    df_ev = datasets.get("waka_kotahi_ev", pd.DataFrame())
    if not df_ev.empty and "_01_P1_EV" in df_ev.columns:
        if "Year" in df_ev.columns:
            latest_year = df_ev["Year"].max()
            total_evs = df_ev[df_ev["Year"] == latest_year]["_01_P1_EV"].sum()
            if latest_year > year_range[0]:
                prev_evs = df_ev[df_ev["Year"] == (latest_year - 1)]["_01_P1_EV"].sum()
                delta = total_evs - prev_evs
                delta_pct = (delta / prev_evs * 100) if prev_evs > 0 else 0
            else:
                delta = 0
                delta_pct = 0
            st.metric(
                "Total EVs on Road",
                f"{int(total_evs):,}",
                f"{int(delta):+,} ({delta_pct:+.1f}%)",
                help="Battery Electric Vehicles currently registered",
            )
        else:
            st.metric("Total EVs on Road", "N/A")
    else:
        st.metric("Total EVs on Road", "N/A")

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
                f"{delta:+.2f}%",
                help="Percentage of total vehicle fleet that is electric",
            )
        else:
            st.metric("Fleet Electrification", "N/A")
    else:
        st.metric("Fleet Electrification", "N/A")

# KPI 3: New EV Sales
with kpi_cols[2]:
    df_new_ev = datasets.get("waka_kotahi_new_ev", pd.DataFrame())
    if not df_new_ev.empty and "_03_P1_NewEV" in df_new_ev.columns:
        if "Year" in df_new_ev.columns:
            latest_year = df_new_ev["Year"].max()
            new_ev_sales = df_new_ev[df_new_ev["Year"] == latest_year][
                "_03_P1_NewEV"
            ].sum()
            if latest_year > year_range[0]:
                prev_sales = df_new_ev[df_new_ev["Year"] == (latest_year - 1)][
                    "_03_P1_NewEV"
                ].sum()
                delta = new_ev_sales - prev_sales
            else:
                delta = 0
            st.metric(
                "New EV Sales",
                f"{int(new_ev_sales):,}",
                f"{int(delta):+,}",
                help="New (not used) EVs purchased in latest year",
            )
        else:
            st.metric("New EV Sales", "N/A")
    else:
        st.metric("New EV Sales", "N/A")

# KPI 4: Used EV Imports
with kpi_cols[3]:
    df_used_ev = datasets.get("waka_kotahi_used_ev", pd.DataFrame())
    if not df_used_ev.empty and "_04_P1_UsedEV" in df_used_ev.columns:
        if "Year" in df_used_ev.columns:
            latest_year = df_used_ev["Year"].max()
            used_ev_imports = df_used_ev[df_used_ev["Year"] == latest_year][
                "_04_P1_UsedEV"
            ].sum()
            if latest_year > year_range[0]:
                prev_imports = df_used_ev[df_used_ev["Year"] == (latest_year - 1)][
                    "_04_P1_UsedEV"
                ].sum()
                delta = used_ev_imports - prev_imports
            else:
                delta = 0
            st.metric(
                "Used EV Imports",
                f"{int(used_ev_imports):,}",
                f"{int(delta):+,}",
                help="Used (imported) EVs purchased in latest year",
            )
        else:
            st.metric("Used EV Imports", "N/A")
    else:
        st.metric("Used EV Imports", "N/A")

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
            st.plotly_chart(fig, width="stretch")
    else:
        st.info("Insufficient data for fleet composition chart")

# Chart 2: Fleet Electrification % Trend
with col2:
    st.subheader("Fleet Electrification % Over Time")

    df_fleet = datasets.get("waka_kotahi_fleet_elec", pd.DataFrame())
    if not df_fleet.empty and "_05_P1_FleetElec" in df_fleet.columns:
        if "Year" in df_fleet.columns and "Region" in df_fleet.columns:
            # Aggregate by year and region
            df_fleet_agg = (
                df_fleet.groupby(["Year", "Region"])["_05_P1_FleetElec"]
                .mean()
                .reset_index()
            )

            # Show top regions
            top_regions = (
                df_fleet_agg.groupby("Region")["_05_P1_FleetElec"]
                .mean()
                .nlargest(10)
                .index
            )
            df_plot = df_fleet_agg[df_fleet_agg["Region"].isin(top_regions)]

            fig = px.line(
                df_plot,
                x="Year",
                y="_05_P1_FleetElec",
                color="Region",
                markers=True,
                labels={"_05_P1_FleetElec": "Fleet Electrification %"},
                color_discrete_sequence=CHART_COLORS,
            )
            st.plotly_chart(fig, width="stretch")
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
            st.plotly_chart(fig, width="stretch")
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
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, width="stretch")
    else:
        st.info("No regional EV data available")

st.markdown("---")

# YoY Growth Analysis
st.subheader("Year-over-Year Growth Analysis")

df_ev = datasets.get("waka_kotahi_ev", pd.DataFrame())
if not df_ev.empty and "_01_P1_EV" in df_ev.columns and "Year" in df_ev.columns:
    df_ev_agg = df_ev.groupby("Year")["_01_P1_EV"].sum().reset_index()
    df_ev_agg = calculate_yoy_growth(df_ev_agg, "_01_P1_EV", ["Year"])

    fig = px.bar(
        df_ev_agg,
        x="Year",
        y="_01_P1_EV_yoy",
        labels={"_01_P1_EV_yoy": "YoY Growth %"},
        color="_01_P1_EV_yoy",
        color_continuous_scale="RdYlGn",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")
else:
    st.info("Insufficient data for YoY growth analysis")

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
    ],
)

dataset_map = {
    "EV Count": "waka_kotahi_ev",
    "Fossil Fuel Vehicles": "waka_kotahi_ff",
    "New EV Sales": "waka_kotahi_new_ev",
    "Used EV Imports": "waka_kotahi_used_ev",
    "Fleet Electrification %": "waka_kotahi_fleet_elec",
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
