"""FastAPI backend for serving metrics.

This API provides endpoints for accessing processed electrification data
from both processed and metrics layers for visualization in dashboards.
"""

from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.repository import DataRepository
from etl.core.config import get_settings

# Initialize FastAPI app
app = FastAPI(
    title="Rewiring Aotearoa Electrification Progress Tracker API",
    description="API for accessing electrification progress data from processed and metrics layers",
    version="0.2.0",
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get settings and repository
settings = get_settings()
repository = DataRepository()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Rewiring Aotearoa Electrification Progress Tracker API",
        "version": "0.2.0",
        "endpoints": {
            "datasets": "/api/datasets",
            "processed": "/api/processed/{dataset}",
            "metrics": "/api/metrics/{dataset}",
            "health": "/health",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/datasets")
async def list_datasets(layer: str = Query("metrics", enum=["processed", "metrics"])):
    """List available datasets in a layer.

    Args:
        layer: Layer to list datasets from (processed or metrics)

    Returns:
        JSON with available datasets
    """
    try:
        datasets = repository.list_datasets(layer=layer)
        return {
            "layer": layer,
            "datasets": datasets,
            "count": len(datasets),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing datasets: {str(e)}")


@app.get("/api/processed/{dataset}")
async def get_processed_data(
    dataset: str,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    filter_json: Optional[str] = None,
):
    """Get data from processed layer with optional filtering.

    Args:
        dataset: Dataset name (e.g., "emi_retail", "eeca", "gic", "emi_generation")
        limit: Maximum number of rows to return
        offset: Number of rows to skip
        filter_json: JSON string of filters (e.g., '{"Year": {"gte": 2020}}')

    Returns:
        JSON with data and metadata
    """
    try:
        import json

        # Parse filters if provided
        filters = json.loads(filter_json) if filter_json else None

        # Query data
        df = repository.query_processed(
            dataset=dataset, filters=filters, limit=limit, offset=offset
        )

        # Get total count (without limit/offset)
        total_rows = repository.count_rows(
            dataset=dataset, layer="processed", filters=filters
        )

        # Convert to records format
        records = df.to_dict(orient="records")

        return {
            "data": records,
            "metadata": {
                "dataset": dataset,
                "layer": "processed",
                "total_rows": total_rows,
                "returned_rows": len(records),
                "offset": offset or 0,
                "limit": limit,
                "columns": list(df.columns),
            },
        }

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset not found. Please run ETL pipeline first. Error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error querying data: {str(e)}"
        ) from e


@app.get("/api/metrics/{dataset}")
async def get_metrics_data(
    dataset: str,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    filter_json: Optional[str] = None,
):
    """Get data from metrics layer with optional filtering.

    Args:
        dataset: Dataset name (e.g., "emi_retail", "eeca", "gic", "emi_generation")
        limit: Maximum number of rows to return
        offset: Number of rows to skip
        filter_json: JSON string of filters (e.g., '{"Year": {"gte": 2020, "lte": 2025}}')

    Returns:
        JSON with data and metadata
    """
    try:
        import json

        # Parse filters if provided
        filters = json.loads(filter_json) if filter_json else None

        # Query data
        df = repository.query_metrics(
            dataset=dataset, filters=filters, limit=limit, offset=offset
        )

        # Get total count (without limit/offset)
        total_rows = repository.count_rows(
            dataset=dataset, layer="metrics", filters=filters
        )

        # Convert to records format
        records = df.to_dict(orient="records")

        return {
            "data": records,
            "metadata": {
                "dataset": dataset,
                "layer": "metrics",
                "total_rows": total_rows,
                "returned_rows": len(records),
                "offset": offset or 0,
                "limit": limit,
                "columns": list(df.columns),
            },
        }

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset not found. Please run ETL pipeline first. Error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error querying data: {str(e)}"
        ) from e


if __name__ == "__main__":
    import uvicorn

    # Run the API
    uvicorn.run(
        "backend.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True,
    )
