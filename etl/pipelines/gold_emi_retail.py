"""Gold layer ETL: Create business-ready aggregated EMI Retail data.

This script transforms silver layer data into business-ready analytics:
- Aggregating data for dashboard consumption
- Creating summary statistics
- Applying business logic
- Optimizing for query performance
"""

from pathlib import Path

import duckdb
import pandas as pd

from etl.core.config import get_settings
from etl.core.medallion import GoldLayer


class EMIRetailGoldProcessor(GoldLayer):
    """Gold layer processor for EMI Retail data."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Process silver data into gold layer.

        Args:
            input_path: Path to silver CSV file
            output_path: Path to save gold CSV file
        """
        print(f"\nReading silver data from: {input_path}")
        df = self.read_csv(input_path)
        print(f"Loaded {len(df)} rows, {len(df.columns)} columns")

        # Display sample of silver data
        print("\nSample of silver data (first 3 rows):")
        print(df.head(3))

        # Business logic and aggregations
        print("\n--- Creating Business-Ready Data ---")

        # Example: Using DuckDB for complex aggregations
        # This is a placeholder - customize based on actual data structure
        print("\n1. Creating aggregated view with DuckDB...")

        # Save temp file for DuckDB
        temp_path = output_path.parent / f"temp_{output_path.name}"
        self.write_csv(df, temp_path)

        # Example aggregation query (adjust based on actual columns)
        # This demonstrates both SQL and the ability to use DuckDB
        aggregation_query = f"""
        SELECT
            *
        FROM read_csv_auto('{temp_path}')
        LIMIT 1000
        """

        try:
            gold_df = self.execute_duckdb_query(aggregation_query)
            print(f"   Created aggregated dataset with {len(gold_df)} rows")
        except Exception as e:
            print(f"   Warning: DuckDB aggregation failed ({e}), using pandas instead")
            # Fallback to pandas processing
            gold_df = df.copy()

        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()

        # Additional pandas-based transformations
        print("\n2. Applying business transformations with pandas...")

        # Example: Add calculated columns, business metrics, etc.
        # This is a placeholder - customize based on business needs
        gold_df["processed_date"] = pd.Timestamp.now().strftime("%Y-%m-%d")
        print(f"   Added metadata columns")

        # Write to gold layer
        print(f"\nWriting {len(gold_df)} rows to gold layer...")
        self.write_csv(gold_df, output_path)

        # Display summary statistics
        print("\n--- Gold Layer Summary ---")
        print(f"Total rows: {len(gold_df)}")
        print(f"Total columns: {len(gold_df.columns)}")
        print(f"\nColumn names: {list(gold_df.columns)}")

        print(f"\n✓ Gold layer processing completed")


def main():
    """Main ETL function for gold layer processing."""
    print("=" * 80)
    print("GOLD LAYER ETL: EMI Retail Business-Ready Data")
    print("=" * 80)

    settings = get_settings()

    # Define input and output paths
    input_path = settings.silver_dir / "emi_retail" / "emi_retail_cleaned.csv"
    output_path = settings.gold_dir / "emi_retail" / "emi_retail_analytics.csv"

    print(f"\nInput (Silver): {input_path}")
    print(f"Output (Gold): {output_path}")

    # Check if input exists
    if not input_path.exists():
        print(f"\n✗ Error: Silver data not found at {input_path}")
        print("  Please run silver_emi_retail.py first")
        return

    # Process data
    processor = EMIRetailGoldProcessor()
    try:
        processor.process(input_path, output_path)
        print(f"\n✓ Gold layer processing completed successfully")
    except Exception as e:
        print(f"\n✗ Gold layer processing failed: {e}")
        raise


if __name__ == "__main__":
    main()
