"""Streamlit dashboard for Electrification Progress data.

Landing page for the multipage Electrification Progress Tracker dashboard.
"""

import os
import sys

import requests
import streamlit as st
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard_utils import add_global_refresh_button

# Load environment variables
load_dotenv()

# Configuration
BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
API_BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

# Page configuration
st.set_page_config(
    page_title="Introduction - Electrification Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


def check_backend_health():
    """Check if backend API is available."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


# Check backend status
backend_healthy = check_backend_health()

# Title and description
st.title("⚡ Rewiring Aotearoa Electrification Progress Tracker")
st.markdown(
    "### Interactive dashboard for comprehensive electrification analysis across New Zealand"
)

if not backend_healthy:
    st.error(
        f"⚠️ Backend API is not available at {API_BASE_URL}. "
        "Please ensure the backend is running."
    )
    st.info("To start the backend, run: `python -m backend.main`")
    st.stop()

st.success("✓ Backend API is connected and healthy")

# Add global refresh button in sidebar
st.sidebar.markdown("## 🔄 Data Management")
add_global_refresh_button(API_BASE_URL)

st.markdown("---")

# Welcome Section
st.markdown("""
## Welcome to the Electrification Progress Tracker

This comprehensive dashboard provides insights into New Zealand's electrification journey across multiple sectors:
transport, energy grid, buildings, and distributed energy resources.

### 📊 Available Analysis Pages

Use the sidebar navigation to explore different aspects of electrification:
""")

# Page descriptions
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 🏠 **Overview Dashboard**
    Holistic view with KPIs across all 14 metrics. See progress indicators, regional maps,
    and normalized comparisons.

    #### 🚗 **Transport Electrification**
    Comprehensive vehicle fleet analysis with district/region toggle. Track EV adoption,
    fleet composition, new vs used EV sales, and year-over-year growth.

    #### ⚡ **Energy Grid**
    Electricity generation mix and renewable energy metrics. Explore electricity share trends,
    renewable generation patterns, and energy consumption by fuel type.

    #### 🏠 **Buildings & Heating**
    Gas connection trends and fossil fuel boiler energy consumption. Monitor the decline
    of gas infrastructure and heating fuel transitions.
    """)

with col2:
    st.markdown("""
    #### ☀️ **Solar & Batteries**
    Distributed energy resource adoption tracking. Analyze solar capacity growth,
    battery penetration rates, and sector-specific adoption patterns.

    #### 🗺️ **Regional Deep Dive**
    Interactive regional comparison with maps and performance matrices. Compare
    regions across multiple electrification indicators.

    #### 📊 **Cross-Sector Analysis**
    Normalized trends and correlation analysis. Understand relationships between
    different electrification metrics using statistical analysis.

    #### 💾 **Data Explorer**
    Browse, filter, and export raw datasets. Access all 14 datasets with pagination,
    search functionality, and CSV export capabilities.
    """)

st.markdown("---")

# Key Features
st.markdown("""
### ✨ Key Features

- **15 Comprehensive Datasets**: EECA, EMI, GIC, and Waka Kotahi data sources
- **District & Region Views**: Toggle between 67 districts and 16 aggregated regions for transport metrics
- **Interactive Visualizations**: Plotly charts with filtering, zooming, and hover details
- **Pagination for Large Datasets**: Efficient handling of 100k+ row datasets
- **Real-time Filtering**: Year range, region, sector, and category filters
- **CSV Export**: Download filtered data from any page
- **Responsive Design**: Optimized for desktop and tablet viewing

### 📈 Metrics Covered

**Transport (6 metrics)**
- EV Count, Fossil Fuel Vehicles, New EV Sales, Used EV Imports, Fleet Electrification %, EV Charging Stations

**Energy Grid (3 metrics)**
- Electricity Share, Renewable Generation, Energy by Fuel Type

**Buildings & Heating (2 metrics)**
- Gas Connections, Fossil Boiler Energy

**Solar & Batteries (4 metrics)**
- Battery Penetration (2 types), Solar Capacity, Battery Capacity

### 🚀 Getting Started

1. **Navigate** using the sidebar to select a page
2. **Filter** data using the sidebar controls on each page
3. **Interact** with charts by hovering, clicking, and zooming
4. **Export** data using the download buttons on each page

### 📊 Data Sources

- **EECA**: Energy Efficiency and Conservation Authority
- **EMI**: Electricity Market Information (Electricity Authority)
- **GIC**: Gas Industry Company
- **Waka Kotahi**: NZ Transport Agency - Motor Vehicle Register

### 🔄 Data Freshness

Data is loaded from the backend API and cached for performance. Use the "Refresh Data"
button in page sidebars to reload with the latest available data.
""")

st.markdown("---")

# Quick Stats
st.markdown("### 📊 Quick Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Datasets",
        value="15",
        help="EECA (4), EMI (4), GIC (1), Waka Kotahi (5), Plus boiler energy",
    )

with col2:
    st.metric(
        label="Analysis Pages",
        value="8",
        help="Overview, Transport, Energy, Buildings, Solar, Regional, Cross-Sector, Data Explorer",
    )

with col3:
    st.metric(
        label="Geographic Regions",
        value="16",
        help="Standard NZ regions, plus 67 districts for transport data",
    )

with col4:
    st.metric(
        label="Year Range",
        value="2010-2025",
        help="Coverage varies by dataset, most comprehensive from 2015+",
    )

st.markdown("---")

st.info("""
💡 **Tip**: Start with the **Overview Dashboard** for a holistic view, then dive into
specific pages for detailed analysis. Use the **Data Explorer** to access raw data for
custom analysis in external tools.
""")

st.caption("""
**Rewiring Aotearoa Electrification Progress Tracker** |
Data sources: EECA, EMI, GIC, Waka Kotahi |
Built with Streamlit & Plotly |
Backend API: FastAPI + DuckDB
""")
