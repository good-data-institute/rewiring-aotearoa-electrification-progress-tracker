"""Gold layer ETL: Create business-ready aggregated EMI Retail data.

This script transforms silver layer data into business-ready analytics:
- Aggregating data for dashboard consumption
- Creating summary statistics
- Applying business logic
- Optimizing for query performance
"""

from pathlib import Path

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

        # Example: Using DuckDB SQL for complex aggregations
        # Maintainers can define ETL logic using SQL queries
        print("\n1. Creating aggregated view with DuckDB SQL...")

        # Save temp file for DuckDB
        temp_path = output_path.parent / f"temp_{output_path.name}"
        self.write_csv(df, temp_path)

        # Example: Complex SQL aggregation query
        # This demonstrates how maintainers can use SQL for ETL transformations
        # Adjust the query based on your actual column names and business logic
        aggregation_query = f"""
        SELECT
            *,
            ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) as row_id
        FROM read_csv_auto('{temp_path}')
        LIMIT 1000
        """

        # Alternative example for time-series aggregation (uncomment and adjust):
        # aggregation_query = f"""
        # SELECT
        #     date_column,
        #     region,
        #     SUM(value) as total_value,
        #     AVG(price) as avg_price,
        #     COUNT(*) as record_count,
        #     MIN(value) as min_value,
        #     MAX(value) as max_value
        # FROM read_csv_auto('{temp_path}')
        # WHERE date_column >= '2020-01-01'
        # GROUP BY date_column, region
        # ORDER BY date_column DESC, region
        # """

        try:
            gold_df = self.execute_duckdb_query(aggregation_query)
            print(f"   ✓ SQL aggregation successful: {len(gold_df)} rows")
        except Exception as e:
            print(f"   ⚠ SQL aggregation failed ({e}), using pandas instead")
            # Fallback to pandas processing
            gold_df = df.copy()

        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()

        # Additional pandas-based transformations
        # Maintainers can mix SQL (DuckDB) and Python (Pandas) as needed
        print("\n2. Applying business transformations with Pandas...")

        # Example: Add calculated columns, business metrics, etc.
        gold_df["processed_date"] = pd.Timestamp.now().strftime("%Y-%m-%d")
        gold_df["data_source"] = "emi_retail"
        print("   ✓ Added metadata columns")

        # Write to gold layer
        print(f"\nWriting {len(gold_df)} rows to gold layer...")
        self.write_csv(gold_df, output_path)

        # Display summary statistics
        print("\n--- Gold Layer Summary ---")
        print(f"Total rows: {len(gold_df)}")
        print(f"Total columns: {len(gold_df.columns)}")
        print(f"\nColumn names: {list(gold_df.columns)}")

        print("\n✓ Gold layer processing completed")


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
        print("\n✓ Gold layer processing completed successfully")
    except Exception as e:
        print(f"\n✗ Gold layer processing failed: {e}")
        raise


if __name__ == "__main__":
    main()
