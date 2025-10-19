"""Streamlit dashboard for EMI Retail electricity data.

A simple dashboard that connects to the FastAPI backend and displays
electrification progress data in an interactive table.
"""

import requests
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
import os

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

# Title and description
st.title("⚡ Rewiring Aotearoa Electrification Progress Tracker")
st.markdown("Dashboard for visualizing electricity market data from EMI Retail")

# Sidebar for controls
st.sidebar.header("Controls")
limit = st.sidebar.slider(
    "Rows to display", min_value=10, max_value=40, value=20, step=1
)
offset = st.sidebar.number_input("Offset", min_value=0, value=0, step=10)

if st.sidebar.button("Refresh Data"):
    st.rerun()


def check_backend_health():
    """Check if backend API is available."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def fetch_data(limit: int = 20, offset: int = 0, test=True):
    """Fetch data from the backend API."""
    if test:
        # Read directly from analytics data
        path = (
            Path(os.getenv("ANALYTICS_DIR", "data/analytics"))
            / "emi"
            / "emi_retail_analytics.csv"
        )
        try:
            df = pd.read_csv(path)
            total_rows = len(df)
            data = df.iloc[offset : offset + limit].to_dict(orient="records")
            return {
                "metadata": {
                    "total_rows": total_rows,
                    "returned_rows": len(data),
                    "offset": offset,
                },
                "data": data,
            }
        except Exception as e:
            st.error(f"Error reading test data: {e}")
            return None
    else:
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/emi-retail",
                params={"limit": limit, "offset": offset},
                timeout=10,
            )
            print("RESPONSE", response)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Error fetching data: {e}")
            return None


# def fetch_summary():
#     """Fetch summary statistics from the backend API."""
#     try:
#         response = requests.get(f"{API_BASE_URL}/api/emi-retail/summary", timeout=10)
#         response.raise_for_status()
#         return response.json()
#     except requests.RequestException as e:
#         st.error(f"Error fetching summary: {e}")
#         return None

# Check backend status
if not check_backend_health():
    st.error(
        f"⚠️ Backend API is not available at {API_BASE_URL}. "
        "Please ensure the backend is running."
    )
    st.info("To start the backend, run: `python -m backend.main`")
    st.stop()

# Backend is healthy
st.success(f"✓ Connected to backend at {API_BASE_URL}")

# Fetch and display summary
# with st.expander("📊 Summary Statistics", expanded=False):
# summary = fetch_summary()
# if summary:
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         st.metric("Total Rows", summary.get("total_rows", "N/A"))
#     with col2:
#         st.metric("Total Columns", summary.get("total_columns", "N/A"))
#     with col3:
#         st.metric("Columns", len(summary.get("columns", [])))

#     st.subheader("Sample Data (First 5 Rows)")
#     if "sample_data" in summary and summary["sample_data"]:
#         sample_df = pd.DataFrame(summary["sample_data"])
#         st.dataframe(sample_df, use_container_width=True)

# Fetch and display main data
st.header("Electricity Market Data")
data_response = fetch_data(limit=limit, offset=offset, test=True)

if data_response:
    metadata = data_response.get("metadata", {})
    data = data_response.get("data", [])

    # Display metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", metadata.get("total_rows", "N/A"))
    with col2:
        st.metric("Showing Rows", metadata.get("returned_rows", "N/A"))
    with col3:
        st.metric("Offset", metadata.get("offset", "N/A"))

    # Display data table
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, height=600)

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download data as CSV",
            data=csv,
            file_name="emi_retail_data.csv",
            mime="text/csv",
        )
    else:
        st.warning("No data available")
else:
    st.error("Failed to fetch data from backend")

# Footer
st.markdown("---")
st.markdown("*Data source: Electricity Authority EMI Retail Portal*")
