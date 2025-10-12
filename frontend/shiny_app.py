"""Shiny for Python dashboard for EMI Retail electricity data.

A simple dashboard that connects to the FastAPI backend and displays
electrification progress data in an interactive table.
"""

import os

import pandas as pd
import requests
from dotenv import load_dotenv
from pathlib import Path
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


def fetch_data(limit: int = 40, offset: int = 0, test=True):
    """Fetch data from the backend API."""
    if test:
        # Read directly from settings.gold_dir / "emi_retail" / "emi_retail_analytics.csv"
        path = (
            Path(os.getenv("GOLD_DIR", "data/gold"))
            / "emi_retail"
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
            return {"error": str(e)}
    else:
        try:
            response = requests.get(
                f"{API_BASE_URL}/api/emi-retail",
                params={"limit": limit, "offset": offset},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}


# def fetch_summary():
#     """Fetch summary statistics from the backend API."""
#     try:
#         response = requests.get(f"{API_BASE_URL}/api/emi-retail/summary", timeout=10)
#         response.raise_for_status()
#         return response.json()
#     except requests.RequestException as e:
#         return {"error": str(e)}


# UI Definition
app_ui = ui.page_fluid(
    ui.panel_title("⚡ Rewiring Aotearoa Electrification Progress Tracker"),
    ui.markdown("Dashboard for visualizing electricity market data from EMI Retail"),
    ui.hr(),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h4("Controls"),
            ui.input_slider(
                "limit", "Rows to display:", min=10, max=50, value=40, step=1
            ),
            ui.input_numeric("offset", "Offset:", value=0, min=0, step=10),
            ui.input_action_button("refresh", "Refresh Data", class_="btn-primary"),
            ui.hr(),
            ui.output_text("backend_status"),
        ),
        ui.h3("Electricity Market Data"),
        ui.output_text("data_info"),
        ui.br(),
        ui.output_data_frame("data_table"),
        ui.br(),
        ui.download_button("download_data", "Download CSV"),
    ),
    ui.hr(),
    ui.markdown("*Data source: Electricity Authority EMI Retail Portal*"),
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
        data_response = fetch_data(limit=input.limit(), offset=input.offset())

        if "error" in data_response:
            return f"Error: {data_response['error']}"

        metadata = data_response.get("metadata", {})
        return (
            f"Total rows: {metadata.get('total_rows', 'N/A')} | "
            f"Showing: {metadata.get('returned_rows', 'N/A')} | "
            f"Offset: {metadata.get('offset', 'N/A')}"
        )

    @output
    @render.data_frame
    def data_table():
        """Render main data table."""
        data_refresh()  # React to refresh
        data_response = fetch_data(limit=input.limit(), offset=input.offset())

        if "error" in data_response:
            return pd.DataFrame({"Error": [data_response["error"]]})

        data = data_response.get("data", [])
        if data:
            return pd.DataFrame(data)
        else:
            return pd.DataFrame({"Message": ["No data available"]})

    @session.download(filename="emi_retail_data.csv")
    def download_data():
        """Download data as CSV."""
        data_response = fetch_data(limit=input.limit(), offset=input.offset())
        data = data_response.get("data", [])
        if data:
            df = pd.DataFrame(data)
            return df.to_csv(index=False)
        return "No data available"


# Create Shiny app
app = App(app_ui, server)
