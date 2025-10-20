"""Streamlit dashboard for Electrification Progress data.

A dashboard that connects to the FastAPI backend and displays
all metrics datasets in interactive tables.
"""

import os

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

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
st.markdown("Dashboard for visualizing electrification progress metrics")

# Sidebar for controls
st.sidebar.header("Controls")
if st.sidebar.button("Refresh Data"):
    st.rerun()


def check_backend_health():
    """Check if backend API is available."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def fetch_datasets():
    """Fetch list of available datasets from backend."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/datasets?layer=metrics", timeout=10
        )
        response.raise_for_status()
        return response.json().get("datasets", [])
    except requests.RequestException as e:
        st.error(f"Error fetching datasets: {e}")
        return []


def fetch_metrics_data(dataset: str, limit: int = 100):
    """Fetch metrics data from the backend API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/metrics/{dataset}",
            params={"limit": limit},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching {dataset} data: {e}")
        return None


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

# Fetch available datasets
datasets = fetch_datasets()

if not datasets:
    st.warning("No metrics datasets found. Please run ETL pipelines first.")
    st.stop()

st.info(f"Found {len(datasets)} metrics datasets: {', '.join(datasets)}")

# Display each dataset
for dataset in datasets:
    st.header(f"📊 {dataset.replace('_', ' ').title()}")

    with st.spinner(f"Loading {dataset}..."):
        data_response = fetch_metrics_data(dataset)

    if data_response:
        metadata = data_response.get("metadata", {})
        data = data_response.get("data", [])

        # Display metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Dataset", metadata.get("dataset", "N/A"))
        with col2:
            st.metric("Total Rows", metadata.get("total_rows", "N/A"))
        with col3:
            st.metric("Showing Rows", metadata.get("returned_rows", "N/A"))

        # Display data table
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, height=400)
        else:
            st.warning(f"No data available for {dataset}")
    else:
        st.error(f"Failed to fetch {dataset} data from backend")

    st.markdown("---")

# Footer
st.markdown("*Data sources: EMI, EECA, GIC*")
