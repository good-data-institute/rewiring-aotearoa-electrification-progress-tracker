"""Medallion architecture layers for data processing."""

from abc import ABC, abstractmethod
from pathlib import Path

import duckdb
import pandas as pd

from etl.core.config import get_settings


class MedallionLayer(ABC):
    """Base class for medallion architecture layers (Bronze, Silver, Gold)."""

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

    def execute_query(self, query: str, input_path: Path | None = None) -> pd.DataFrame:
        """Execute a DuckDB query and return results as DataFrame.

        Args:
            query: SQL query to execute
            input_path: Optional path to CSV file to query

        Returns:
            DataFrame with query results
        """
        con = duckdb.connect(":memory:")

        if input_path:
            # Register the CSV file as a table
            table_name = input_path.stem
            con.execute(
                f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{input_path}')"
            )

        result = con.execute(query).fetchdf()
        con.close()

        return result


# class BronzeLayer(MedallionLayer):
#     """Bronze layer: Raw data ingestion."""

#     def process(self, input_path: Path, output_path: Path) -> None:
#         """Copy raw data to bronze layer.

#         Args:
#             input_path: Path to raw data file
#             output_path: Path to save in bronze layer
#         """
#         output_path.parent.mkdir(parents=True, exist_ok=True)

#         # For bronze, we typically just copy/move the raw data
#         df = self.read_csv(input_path)
#         print(f"Bronze layer: Loaded {len(df)} rows from {input_path}")

#         self.write_csv(df, output_path)


class SilverLayer(MedallionLayer):
    """Silver layer: Cleaned and validated data."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Clean and validate data for silver layer.

        Args:
            input_path: Path to bronze data
            output_path: Path to save in silver layer
        """
        # Default implementation - override in specific processors
        df = self.read_csv(input_path)
        print(f"Silver layer: Processing {len(df)} rows from {input_path}")

        # Basic cleaning: remove duplicates, handle nulls
        df = df.drop_duplicates()
        print(f"Silver layer: {len(df)} rows after deduplication")

        self.write_csv(df, output_path)


class GoldLayer(MedallionLayer):
    """Gold layer: Business-ready aggregated data."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Aggregate data for gold layer.

        Args:
            input_path: Path to silver data
            output_path: Path to save in gold layer
        """
        # Default implementation - override in specific processors
        df = self.read_csv(input_path)
        print(f"Gold layer: Processing {len(df)} rows from {input_path}")

        # This is where business logic and aggregations would go
        self.write_csv(df, output_path)
