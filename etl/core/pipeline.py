"""Data processing layers for ETL pipelines.

This module provides base classes for a 2-layer data architecture:
- DataLayer: Extract from source + Transform/Clean
- AnalyticsLayer: Business-ready analytics and aggregations
"""

from abc import ABC, abstractmethod
from pathlib import Path

import duckdb
import pandas as pd

from etl.core.config import get_settings


class BaseLayer(ABC):
    """Base class for data processing layers."""

    def __init__(self):
        """Initialize the layer with settings."""
        self.settings = get_settings()

    @abstractmethod
    def process(self, input_path: Path, output_path: Path) -> None:
        """Process data for this layer.

        Args:
            input_path: Path to input data
            output_path: Path to save processed data
        """
        pass

    def read_csv(self, path: Path, skiprows: int = 0) -> pd.DataFrame:
        """Read CSV file into pandas DataFrame.

        Args:
            path: Path to CSV file
            skiprows: Number of rows to skip at start of file

        Returns:
            DataFrame with CSV data
        """
        return pd.read_csv(path, skiprows=skiprows)

    def write_csv(self, df: pd.DataFrame, path: Path) -> None:
        """Write DataFrame to CSV file.

        Args:
            df: DataFrame to write
            path: Path to output CSV file
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        print(f"Data written to: {path}")

    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a DuckDB query and return results as DataFrame.

        This method is preferred for SQL-based transformations.
        DuckDB can read CSV files directly using read_csv_auto().

        Args:
            query: SQL query to execute

        Returns:
            DataFrame with query results

        Example:
            query = "SELECT * FROM read_csv_auto('data/file.csv') WHERE value > 100"
            df = self.execute_query(query)
        """
        con = duckdb.connect(":memory:")
        result = con.execute(query).fetchdf()
        con.close()
        return result


class DataLayer(BaseLayer):
    """Data layer: Extract from source and transform/clean data.

    This layer combines data extraction and transformation:
    - Fetches data from external APIs or sources
    - Cleans and validates data
    - Removes duplicates
    - Standardizes formats
    - Saves processed data
    """

    def process(self, input_path: Path, output_path: Path) -> None:
        """Extract and transform data.

        Override this method in your specific processor to:
        1. Fetch data from API or source
        2. Clean and validate
        3. Write output

        Args:
            input_path: Not used for extraction, kept for interface compatibility
            output_path: Path to save processed data
        """
        raise NotImplementedError("Subclasses must implement process() method")


class AnalyticsLayer(BaseLayer):
    """Analytics layer: Business-ready aggregated data.

    This layer creates analytics-ready data:
    - Aggregations and metrics
    - Business logic
    - Optimized for dashboard queries
    """

    def process(self, input_path: Path, output_path: Path) -> None:
        """Create analytics from processed data.

        Override this method in your specific processor to:
        1. Read from processed data
        2. Apply business logic and aggregations
        3. Write analytics output

        Args:
            input_path: Path to input data
            output_path: Path to save analytics
        """
        raise NotImplementedError("Subclasses must implement process() method")
