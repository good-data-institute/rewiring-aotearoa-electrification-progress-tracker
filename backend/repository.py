"""Data repository for querying processed and metrics data using DuckDB.

This module provides a repository pattern implementation for accessing
data layers with support for filtering and querying.
"""

from typing import Any, Dict, List, Optional

import duckdb
import pandas as pd

from etl.core.config import get_settings


class DataRepository:
    """Repository for querying data from processed and metrics layers using DuckDB."""

    def __init__(self):
        """Initialize repository with settings."""
        self.settings = get_settings()
        self._connection = None
        self.s3_base = "https://test-gdi-28924.s3.amazonaws.com/data"

    @property
    def connection(self):
        """Get or create DuckDB connection."""
        if self._connection is None:
            self._connection = duckdb.connect(":memory:")
            self._connection.execute("INSTALL httpfs;")
            self._connection.execute("LOAD httpfs;")
        return self._connection

    def _build_where_clause(self, filters: Optional[Dict[str, Any]]) -> str:
        """Build SQL WHERE clause from filters.

        Args:
            filters: Dictionary of column: value pairs for filtering

        Returns:
            SQL WHERE clause string
        """
        if not filters:
            return ""

        conditions = []
        for column, value in filters.items():
            if isinstance(value, str):
                conditions.append(f"{column} = '{value}'")
            elif isinstance(value, (int, float)):
                conditions.append(f"{column} = {value}")
            elif isinstance(value, dict):
                # Handle range filters like {"gte": 2020, "lte": 2025}
                if "gte" in value:
                    conditions.append(f"{column} >= {value['gte']}")
                if "lte" in value:
                    conditions.append(f"{column} <= {value['lte']}")
                if "gt" in value:
                    conditions.append(f"{column} > {value['gt']}")
                if "lt" in value:
                    conditions.append(f"{column} < {value['lt']}")

        if conditions:
            return " WHERE " + " AND ".join(conditions)
        return ""

    def query_processed(
        self,
        dataset: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> pd.DataFrame:
        """Query data from processed layer.

        Args:
            dataset: Dataset name (e.g., "demo_emi_retail", "eeca", "gic", "emi_generation")
            filters: Dictionary of filters to apply
            limit: Maximum number of rows to return
            offset: Number of rows to skip

        Returns:
            DataFrame with query results

        Raises:
            FileNotFoundError: If dataset file doesn't exist
        """
        # Determine file path based on dataset
        file_mapping = {
            "demo_emi_retail": self.settings.processed_dir
            / "demo_emi_retail"
            / "demo_emi_retail_cleaned.csv",
            "eeca": self.settings.processed_dir
            / "eeca"
            / "eeca_energy_consumption_cleaned.csv",
            "gic": self.settings.processed_dir
            / "gic"
            / "gic_gas_connections_cleaned.csv",
            "emi_generation": self.settings.processed_dir
            / "emi_generation"
            / "emi_generation_cleaned.csv",
        }

        file_path = file_mapping.get(dataset)
        if not file_path:
            raise ValueError(f"Unknown dataset: {dataset}")

        if not file_path.exists():
            raise FileNotFoundError(f"Processed data not found: {file_path}")

        # Build query
        where_clause = self._build_where_clause(filters)
        limit_clause = f" LIMIT {limit}" if limit else ""
        offset_clause = f" OFFSET {offset}" if offset else ""

        query = f"""
        SELECT *
        FROM read_csv_auto('{file_path}')
        {where_clause}
        {limit_clause}
        {offset_clause}
        """

        # Execute query
        return self.connection.execute(query).df()

    def query_metrics(
        self,
        dataset: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> pd.DataFrame:
        """Query data from metrics layer on S3.

        Args:
            dataset: Dataset name (e.g., "eeca_electricity_percentage", "gic_analytics", "emi_generation_analytics")
            filters: Dictionary of filters to apply
            limit: Maximum number of rows to return
            offset: Number of rows to skip

        Returns:
            DataFrame with query results

        Raises:
            ValueError: If dataset is unknown
        """
        # Map dataset names to S3 CSV URLs
        file_mapping = {
            "eeca_electricity_percentage": f"{self.s3_base}/metrics/eeca/eeca_electricity_percentage.csv",
            "eeca_energy_by_fuel": f"{self.s3_base}/metrics/eeca/eeca_energy_by_fuel.csv",
            "gic_analytics": f"{self.s3_base}/metrics/gic/gic_gas_connections_analytics.csv",
            "emi_generation_analytics": f"{self.s3_base}/metrics/emi_generation/emi_generation_analytics.csv",
            "battery_penetration_commercial": f"{self.s3_base}/metrics/emi_battery_solar/_06a_P1_BattPen.csv",
            "battery_penetration_residential": f"{self.s3_base}/metrics/emi_battery_solar/_06b_P1_BattPen.csv",
            "solar_penetration": f"{self.s3_base}/metrics/emi_battery_solar/_07_P1_Sol.csv",
        }

        s3_url = file_mapping.get(dataset)
        if not s3_url:
            raise ValueError(f"Unknown dataset: {dataset}")

        # Build query
        where_clause = self._build_where_clause(filters)
        limit_clause = f" LIMIT {limit}" if limit else ""
        offset_clause = f" OFFSET {offset}" if offset else ""

        query = f"""
        SELECT *
        FROM read_csv_auto('{s3_url}')
        {where_clause}
        {limit_clause}
        {offset_clause}
        """

        # Execute query
        return self.connection.execute(query).df()

    def list_datasets(self, layer: str = "metrics") -> List[str]:
        """List available datasets in a layer.

        Args:
            layer: Layer to list datasets from ("processed" or "metrics")

        Returns:
            List of dataset names
        """
        if layer == "metrics":
            # Return hardcoded list of available S3 datasets
            return [
                "eeca_electricity_percentage",
                "eeca_energy_by_fuel",
                "gic_analytics",
                "emi_generation_analytics",
                "battery_penetration_commercial",
                "battery_penetration_residential",
                "solar_penetration",
            ]
        elif layer == "processed":
            # Processed layer not available on S3 yet
            return []
        else:
            return []

    def get_schema(self, dataset: str, layer: str = "metrics") -> Dict[str, str]:
        """Get schema (column names and types) for a dataset.

        Args:
            dataset: Dataset name
            layer: Layer to query ("processed" or "metrics")

        Returns:
            Dictionary of column names and types
        """
        try:
            if layer == "processed":
                df = self.query_processed(dataset, limit=1)
            else:
                df = self.query_metrics(dataset, limit=1)

            return {col: str(dtype) for col, dtype in df.dtypes.items()}
        except Exception:
            return {}

    def count_rows(
        self,
        dataset: str,
        layer: str = "metrics",
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Count total rows in a dataset.

        Args:
            dataset: Dataset name
            layer: Layer to query ("processed" or "metrics")
            filters: Optional filters to apply

        Returns:
            Total row count
        """
        try:
            if layer == "processed":
                df = self.query_processed(dataset, filters=filters)
            else:
                df = self.query_metrics(dataset, filters=filters)

            return len(df)
        except Exception:
            return 0

    def close(self):
        """Close the DuckDB connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
