"""FastAPI backend for serving gold layer data.

This API provides endpoints for accessing processed electrification data
from the gold layer for visualization in dashboards.
"""

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
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - checks if docs endpoint is alive."""
    try:
        # Check if the docs endpoint (/) is working
        await root()
        return {
            "status": "healthy",
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.get("/api/emi-retail")
async def get_emi_retail_data(limit: int = 40, offset: int = 0):
    """Get EMI retail electricity data from analytics.

    Args:
        limit: Maximum number of rows to return (default 40)
        offset: Number of rows to skip (default 0)

    Returns:
        JSON with data and metadata
    """
    analytics_data_path = settings.analytics_dir / "emi" / "emi_retail_analytics.csv"

    # Check if data exists
    if not analytics_data_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Analytics data not found. Please run ETL pipeline first. "
            f"Expected path: {analytics_data_path}",
        )

    try:
        # Read data
        df = pd.read_csv(analytics_data_path)

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


if __name__ == "__main__":
    import uvicorn

    # Run the API
    uvicorn.run(
        "backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
