"""Shiny for Python dashboard for Electrification Progress data.

A dashboard that connects to the FastAPI backend and displays
all metrics datasets in interactive tables.
"""

import os

import pandas as pd
import requests
from dotenv import load_dotenv
from shiny import App, reactive, render, ui

# Load environment variables
load_dotenv()

# Configuration
BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
API_BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"


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
    except requests.RequestException:
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
        return {"error": str(e)}


# Get available datasets at startup
AVAILABLE_DATASETS = fetch_datasets()

# UI Definition
app_ui = ui.page_fluid(
    ui.panel_title("⚡ Rewiring Aotearoa Electrification Progress Tracker"),
    ui.markdown("Dashboard for visualizing electrification progress metrics"),
    ui.hr(),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h4("Controls"),
            ui.input_select(
                "dataset",
                "Select Dataset:",
                choices={ds: ds.replace("_", " ").title() for ds in AVAILABLE_DATASETS}
                if AVAILABLE_DATASETS
                else {"none": "No datasets available"},
                selected=AVAILABLE_DATASETS[0] if AVAILABLE_DATASETS else "none",
            ),
            ui.input_slider(
                "limit", "Rows to display:", min=10, max=100, value=50, step=10
            ),
            ui.input_action_button("refresh", "Refresh Data", class_="btn-primary"),
            ui.hr(),
            ui.output_text("backend_status"),
        ),
        ui.h3("Metrics Data"),
        ui.output_text("data_info"),
        ui.br(),
        ui.output_data_frame("data_table"),
    ),
    ui.hr(),
    ui.markdown("*Data sources: EMI, EECA, GIC*"),
)


# Server logic
def server(input, output, session):
    """Shiny server logic."""

    # Reactive value for data refresh
    data_refresh = reactive.Value(0)

    @reactive.effect
    @reactive.event(input.refresh)
    def _():
        data_refresh.set(data_refresh() + 1)

    @output
    @render.text
    def backend_status():
        """Display backend connection status."""
        data_refresh()  # React to refresh
        if check_backend_health():
            return f"✓ Connected to backend at {API_BASE_URL}"
        else:
            return f"⚠️ Backend not available at {API_BASE_URL}"

    @output
    @render.text
    def data_info():
        """Display data metadata."""
        data_refresh()  # React to refresh
        dataset = input.dataset()

        if dataset == "none":
            return "No datasets available"

        data_response = fetch_metrics_data(dataset, limit=input.limit())

        if "error" in data_response:
            return f"Error: {data_response['error']}"

        metadata = data_response.get("metadata", {})
        return (
            f"Dataset: {metadata.get('dataset', 'N/A')} | "
            f"Total rows: {metadata.get('total_rows', 'N/A')} | "
            f"Showing: {metadata.get('returned_rows', 'N/A')}"
        )

    @output
    @render.data_frame
    def data_table():
        """Render main data table."""
        data_refresh()  # React to refresh
        dataset = input.dataset()

        if dataset == "none":
            return pd.DataFrame(
                {"Message": ["No datasets available. Please run ETL pipelines."]}
            )

        data_response = fetch_metrics_data(dataset, limit=input.limit())

        if "error" in data_response:
            return pd.DataFrame({"Error": [data_response["error"]]})

        data = data_response.get("data", [])
        if data:
            return pd.DataFrame(data)
        else:
            return pd.DataFrame({"Message": ["No data available"]})


# Create Shiny app
app = App(app_ui, server)
