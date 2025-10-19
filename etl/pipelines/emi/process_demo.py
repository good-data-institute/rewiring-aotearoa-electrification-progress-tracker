"""Analytics: EMI Retail gold layer pipeline.

This script creates business-ready analytics from silver layer data:
- Aggregations and summary statistics
- Business logic and calculated metrics
- Data optimized for dashboard consumption
"""

from pathlib import Path

import pandas as pd

from etl.core.config import get_settings
from etl.core.pipeline import AnalyticsLayer


class DemoProcessor(AnalyticsLayer):
    """Analytics layer processor for EMI Retail (Gold layer)."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Process silver data into gold layer analytics.

        Args:
            input_path: Path to silver CSV file
            output_path: Path to save gold CSV file
        """
        print(f"\n{'='*80}")
        print("EMI RETAIL: Analytics Layer (Gold)")
        print(f"{'='*80}")

        # Step 1: Load silver data
        print("\n[1/3] Loading silver data...")
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

            gold_df = self.execute_query(aggregation_query)
            print(f"      ✓ SQL aggregation created {len(gold_df)} rows")

        except Exception as e:
            print(f"      ⚠ SQL aggregation skipped ({e})")
            print("      → Using pandas processing instead")
            gold_df = df.copy()

        # Option 2: Additional Pandas transformations
        print("      - Applying business logic with Pandas...")

        # Add metadata columns
        gold_df["processed_date"] = pd.Timestamp.now().strftime("%Y-%m-%d")
        gold_df["data_source"] = "emi_retail"
        print("      ✓ Added metadata columns")

        # Add any custom business metrics here
        # Example:
        # gold_df['cost_category'] = pd.cut(
        #     gold_df['total_cost'],
        #     bins=[0, 100, 500, float('inf')],
        #     labels=['Low', 'Medium', 'High']
        # )

        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()

        # Step 3: Save to gold layer
        print("\n[3/3] Saving to gold layer...")
        self.write_csv(gold_df, output_path)

        # Summary statistics
        print(f"\n{'='*80}")
        print("✓ COMPLETED: Gold layer analytics ready")
        print(f"  Rows: {len(gold_df)}")
        print(f"  Columns: {len(gold_df.columns)}")
        print(f"  Column names: {list(gold_df.columns)[:10]}...")
        print(f"  Output: {output_path}")
        print(f"{'='*80}\n")


def main():
    """Main function to run the analytics pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = settings.silver_dir / "emi" / "emi_retail_cleaned.csv"
    output_path = settings.gold_dir / "emi" / "emi_retail_analytics.csv"

    print(f"Input (Silver): {input_path}")
    print(f"Output (Gold): {output_path}")

    # Check if input exists
    if not input_path.exists():
        print(f"\n✗ Error: Silver data not found at {input_path}")
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
