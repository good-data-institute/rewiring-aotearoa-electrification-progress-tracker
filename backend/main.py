"""FastAPI backend for serving metrics.

This API provides endpoints for accessing processed electrification data
from both processed and metrics layers for visualization in dashboards.
"""

import logging
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.metadata import get_all_metadata, get_metadata, get_metadata_by_sector
from backend.repository import DataRepository
from etl.core.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_df_to_json_serializable(df: pd.DataFrame) -> list:
    """Convert DataFrame to JSON-serializable list of records.

    Handles:
    - NaN/NA values -> empty string
    - Timestamp/datetime objects -> ISO format strings

    Args:
        df: DataFrame to convert

    Returns:
        List of dictionaries ready for JSON serialization
    """
    # Make a copy to avoid modifying original
    df_copy = df.copy()

    # Convert datetime/timestamp columns to strings
    for col in df_copy.columns:
        if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Replace NaN with empty string and convert to records
    records = df_copy.replace({pd.NA: ""}).fillna(value="").to_dict(orient="records")

    return records


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
        logger.error(f"Error listing datasets for layer {layer}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error listing datasets: {str(e)}"
        ) from e


@app.get("/api/metrics/metadata")
async def get_all_metrics_metadata():
    """Get metadata for all metrics.

    Returns:
        JSON with metadata for all metrics, optionally grouped by sector
    """
    try:
        all_metadata = get_all_metadata()
        return {
            "metrics": {
                key: metadata.to_dict() for key, metadata in all_metadata.items()
            },
            "count": len(all_metadata),
        }
    except Exception as e:
        logger.error("Error retrieving metrics metadata", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error retrieving metadata: {str(e)}"
        ) from e


@app.get("/api/metrics/metadata/by-sector")
async def get_metrics_metadata_by_sector():
    """Get metadata for all metrics grouped by sector.

    Returns:
        JSON with metadata grouped by sector
    """
    try:
        by_sector = get_metadata_by_sector()
        return {
            "sectors": {
                sector: [m.to_dict() for m in metrics]
                for sector, metrics in by_sector.items()
            },
            "count": len(by_sector),
        }
    except Exception as e:
        logger.error("Error retrieving metrics metadata by sector", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error retrieving metadata: {str(e)}"
        ) from e


@app.get("/api/metrics/{dataset}/metadata")
async def get_dataset_metadata(dataset: str):
    """Get metadata for a specific dataset.

    Args:
        dataset: Dataset key

    Returns:
        JSON with metadata for the specified dataset
    """
    try:
        metadata = get_metadata(dataset)
        if not metadata:
            raise HTTPException(
                status_code=404, detail=f"Metadata not found for dataset: {dataset}"
            )
        return metadata.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving metadata for {dataset}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error retrieving metadata: {str(e)}"
        ) from e


@app.get("/api/processed/{dataset}")
async def get_processed_data(
    dataset: str,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    filter_json: Optional[str] = None,
):
    """Get data from processed layer with optional filtering.

    Args:
        dataset: Dataset name (e.g., "demo_emi_retail", "eeca", "gic", "emi_generation")
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

        # Convert to records format, handling timestamps and NaN values
        records = convert_df_to_json_serializable(df)

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
        logger.error(f"Processed dataset not found: {dataset}", exc_info=True)
        raise HTTPException(
            status_code=404,
            detail=f"Dataset not found. Please run ETL pipeline first. Error: {str(e)}",
        ) from e
    except Exception as e:
        logger.error(f"Error querying processed data for {dataset}", exc_info=True)
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
        dataset: Dataset name (e.g., "demo_emi_retail", "eeca", "gic", "emi_generation")
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

        # Convert to records format, handling timestamps and NaN values
        records = convert_df_to_json_serializable(df)

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
        logger.error(f"Dataset not found: {dataset}", exc_info=True)
        raise HTTPException(
            status_code=404,
            detail=f"Dataset not found. Please run ETL pipeline first. Error: {str(e)}",
        ) from e
    except Exception as e:
        logger.error(f"Error querying metrics data for {dataset}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error querying data: {str(e)}"
        ) from e


@app.post("/api/metrics/{dataset}/refresh")
async def refresh_metric(dataset: str):
    """Signal that metric cache should be refreshed.

    This endpoint doesn't run any ETL pipelines - it just provides a hook
    for the frontend to know when to invalidate its cache and re-fetch data.

    Args:
        dataset: Dataset key to refresh

    Returns:
        JSON with refresh acknowledgment
    """
    try:
        # Get metadata for the dataset
        metadata = get_metadata(dataset)
        if not metadata:
            raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset}")

        logger.info(f"Cache refresh requested for metric: {dataset}")

        return {
            "status": "success",
            "dataset": dataset,
            "metric_id": metadata.metric_id,
            "friendly_name": metadata.friendly_name,
            "message": f"Cache refresh triggered for {metadata.friendly_name}",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing refresh request for {dataset}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error processing refresh: {str(e)}"
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
