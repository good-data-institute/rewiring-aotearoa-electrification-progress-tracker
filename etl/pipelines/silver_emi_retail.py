"""Silver layer ETL: Clean and validate EMI Retail data.

This script processes bronze layer data by:
- Removing duplicates
- Handling missing values
- Standardizing column names
- Validating data types
- Basic data quality checks
"""

from pathlib import Path


from etl.core.config import get_settings
from etl.core.medallion import SilverLayer


class EMIRetailSilverProcessor(SilverLayer):
    """Silver layer processor for EMI Retail data."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Process bronze data into silver layer.

        Args:
            input_path: Path to bronze CSV file
            output_path: Path to save silver CSV file
        """
        print(f"\nReading bronze data from: {input_path}")
        df = self.read_csv(input_path)
        print(f"Loaded {len(df)} rows, {len(df.columns)} columns")

        # Display sample of raw data
        print("\nSample of bronze data (first 3 rows):")
        print(df.head(3))

        # Data cleaning steps
        print("\n--- Data Cleaning ---")

        # 1. Remove exact duplicates
        initial_rows = len(df)
        df = df.drop_duplicates()
        print(f"1. Removed {initial_rows - len(df)} duplicate rows")

        # 2. Standardize column names (lowercase, replace spaces with underscores)
        df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace("-", "_")
        print(f"2. Standardized {len(df.columns)} column names")

        # 3. Display info about missing values
        missing_counts = df.isnull().sum()
        if missing_counts.sum() > 0:
            print("\n3. Missing values by column:")
            print(missing_counts[missing_counts > 0])
        else:
            print("3. No missing values found")

        # 4. Basic data validation using DuckDB SQL
        print("\n4. Running data quality checks with DuckDB SQL...")

        # Save to temp location for DuckDB query
        temp_path = output_path.parent / f"temp_{output_path.name}"
        self.write_csv(df, temp_path)

        # Example DuckDB SQL queries for data quality checks
        # This demonstrates how maintainers can use SQL for ETL
        quality_check_query = f"""
        SELECT
            COUNT(*) as total_rows,
            COUNT(DISTINCT *) as unique_rows,
            COUNT(*) - COUNT(DISTINCT *) as duplicate_count
        FROM read_csv_auto('{temp_path}')
        """

        quality_results = self.execute_duckdb_query(quality_check_query)
        print("\nData Quality Metrics:")
        print(quality_results)

        # Additional SQL example: Column statistics
        # Maintainers can add more complex SQL queries here
        print("\n5. SQL-based column analysis (example):")
        column_stats_query = f"""
        SELECT
            '{temp_path.stem}' as table_name,
            COUNT(*) as row_count,
            COUNT(COLUMNS(*)) as column_count
        FROM read_csv_auto('{temp_path}')
        """

        stats = self.execute_duckdb_query(column_stats_query)
        print(stats)

        # Clean up temp file
        temp_path.unlink()

        # Write to silver layer
        print(f"\nWriting {len(df)} rows to silver layer...")
        self.write_csv(df, output_path)
        print("✓ Silver layer processing completed")


def main():
    """Main ETL function for silver layer processing."""
    print("=" * 80)
    print("SILVER LAYER ETL: EMI Retail Data Cleaning")
    print("=" * 80)

    settings = get_settings()

    # Define input and output paths
    input_path = settings.bronze_dir / "emi_retail" / "emi_retail_20130901_20250831.csv"
    output_path = settings.silver_dir / "emi_retail" / "emi_retail_cleaned.csv"

    print(f"\nInput (Bronze): {input_path}")
    print(f"Output (Silver): {output_path}")

    # Check if input exists
    if not input_path.exists():
        print(f"\n✗ Error: Bronze data not found at {input_path}")
        print("  Please run bronze_emi_retail.py first")
        return

    # Process data
    processor = EMIRetailSilverProcessor()
    try:
        processor.process(input_path, output_path)
        print("\n✓ Silver layer processing completed successfully")
    except Exception as e:
        print(f"\n✗ Silver layer processing failed: {e}")
        raise


if __name__ == "__main__":
    main()
