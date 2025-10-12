"""FastAPI backend for serving gold layer data.

This API provides endpoints for accessing processed electrification data
from the gold layer for visualization in dashboards.
"""

from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from etl.core.config import get_settings

# Initialize FastAPI app
app = FastAPI(
    title="Rewiring Aotearoa Electrification Progress Tracker API",
    description="API for accessing electrification progress data",
    version="0.1.0",
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get settings
settings = get_settings()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Rewiring Aotearoa Electrification Progress Tracker API",
        "version": "0.1.0",
        "endpoints": {
            "/health": "Health check",
            "/api/emi-retail": "Get EMI retail electricity data",
            "/api/emi-retail/summary": "Get summary statistics",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    gold_data_path = settings.gold_dir / "emi_retail" / "emi_retail_analytics.csv"
    data_available = gold_data_path.exists()

    return {
        "status": "healthy",
        "data_available": data_available,
        "gold_layer_path": str(gold_data_path),
    }


@app.get("/api/emi-retail")
async def get_emi_retail_data(limit: int = 100, offset: int = 0):
    """Get EMI retail electricity data from gold layer.

    Args:
        limit: Maximum number of rows to return (default 100)
        offset: Number of rows to skip (default 0)

    Returns:
        JSON with data and metadata
    """
    gold_data_path = settings.gold_dir / "emi_retail" / "emi_retail_analytics.csv"

    # Check if data exists
    if not gold_data_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Gold layer data not found. Please run ETL pipeline first. "
            f"Expected path: {gold_data_path}",
        )

    try:
        # Read data
        df = pd.read_csv(gold_data_path)

        # Apply pagination
        total_rows = len(df)
        df_paginated = df.iloc[offset : offset + limit]

        # Convert to records format
        records = df_paginated.to_dict(orient="records")

        return {
            "data": records,
            "metadata": {
                "total_rows": total_rows,
                "returned_rows": len(records),
                "offset": offset,
                "limit": limit,
                "columns": list(df.columns),
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading data: {str(e)}")


@app.get("/api/emi-retail/summary")
async def get_emi_retail_summary():
    """Get summary statistics for EMI retail data.

    Returns:
        JSON with summary statistics
    """
    gold_data_path = settings.gold_dir / "emi_retail" / "emi_retail_analytics.csv"

    # Check if data exists
    if not gold_data_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Gold layer data not found. Please run ETL pipeline first.",
        )

    try:
        # Read data
        df = pd.read_csv(gold_data_path)

        # Generate summary statistics
        summary = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "sample_data": df.head(5).to_dict(orient="records"),
        }

        # Add numeric column statistics if available
        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
        if len(numeric_cols) > 0:
            summary["numeric_summary"] = df[numeric_cols].describe().to_dict()

        return summary

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    # Run the API
    uvicorn.run(
        "backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
