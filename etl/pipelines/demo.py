"""Analytics: EMI Retail analytics pipeline.

This script creates business-ready analytics from processed data:
- Aggregations and transformations
- Business logic and calculated metrics
- Data optimized for dashboard consumption
"""

from pathlib import Path

import pandas as pd

from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer


class DemoProcessor(MetricsLayer):
    """Analytics processor for EMI Retail."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Create analytics from processed data.

        Args:
            input_path: Path to processed CSV file
            output_path: Path to save analytics CSV file
        """
        print(f"\n{'='*80}")
        print("EMI RETAIL: Create Analytics")
        print(f"{'='*80}")

        # Step 1: Load processed data
        print("\n[1/3] Loading processed data...")
        print(f"      Input: {input_path}")
        df = self.read_csv(input_path)
        print(f"      ✓ Loaded {len(df)} rows, {len(df.columns)} columns")

        # Display sample
        print("\n      Sample data (first 3 rows):")
        print(df.head(3).to_string(index=False))

        # Step 2: Create analytics using SQL and/or Pandas
        print("\n[2/3] Creating business-ready analytics...")

        # Save temp file for DuckDB SQL queries
        temp_path = output_path.parent / f"temp_{output_path.name}"
        self.write_csv(df, temp_path)

        # Option 1: Use DuckDB SQL for complex aggregations
        # Example query - customize based on your actual columns
        print("      - Running SQL aggregations...")

        try:
            aggregation_query = f"""
            SELECT
                *,
                ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) as row_id
            FROM read_csv_auto('{temp_path}')
            LIMIT 1000
            """

            # Alternative: Time-series aggregation example
            # Uncomment and adjust based on your actual column names:
            # aggregation_query = f"""
            # SELECT
            #     DATE_TRUNC('month', date_column) as month,
            #     region,
            #     SUM(consumption) as total_consumption,
            #     AVG(price) as avg_price,
            #     COUNT(*) as record_count,
            #     MIN(consumption) as min_consumption,
            #     MAX(consumption) as max_consumption
            # FROM read_csv_auto('{temp_path}')
            # WHERE date_column >= '2020-01-01'
            # GROUP BY DATE_TRUNC('month', date_column), region
            # ORDER BY month DESC, region
            # """

            analytics_df = self.execute_query(aggregation_query)
            print(f"      ✓ SQL aggregation created {len(analytics_df)} rows")

        except Exception as e:
            print(f"      ⚠ SQL aggregation skipped ({e})")
            print("      → Using pandas processing instead")
            analytics_df = df.copy()

        # Option 2: Additional Pandas transformations
        print("      - Applying business logic with Pandas...")

        # Add metadata columns
        analytics_df["processed_date"] = pd.Timestamp.now().strftime("%Y-%m-%d")
        analytics_df["data_source"] = "demo_emi_retail"
        print("      ✓ Added metadata columns")

        # Add any custom business metrics here
        # Example:
        # analytics_df['cost_category'] = pd.cut(
        #     analytics_df['total_cost'],
        #     bins=[0, 100, 500, float('inf')],
        #     labels=['Low', 'Medium', 'High']
        # )

        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()

        # Step 3: Save analytics
        print("\n[3/3] Saving analytics...")
        self.write_csv(analytics_df, output_path)

        print(f"\n{'='*80}")
        print("✓ COMPLETED: Analytics ready")
        print(f"  Rows: {len(analytics_df)}")
        print(f"  Columns: {len(analytics_df.columns)}")
        print(f"  Column names: {list(analytics_df.columns)[:10]}...")
        print(f"  Output: {output_path}")
        print(f"{'='*80}\n")


def main():
    """Main function to run the analytics pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = settings.processed_dir / "demo_emi_retail" / "emi_retail_cleaned.csv"
    output_path = settings.metrics_dir / "demo_emi_retail" / "emi_retail_analytics.csv"

    print(f"Input: {input_path}")
    print(f"Output: {output_path}")

    # Check if input exists
    if not input_path.exists():
        print(f"\n✗ Error: Processed data not found at {input_path}")
        print("  Please run extract_transform.py first")
        return

    # Create processor and run
    processor = DemoProcessor()

    try:
        processor.process(input_path, output_path)
    except Exception as e:
        print(f"\n✗ Analytics processing failed: {e}")
        raise


if __name__ == "__main__":
    main()
