"""Transform: EMI Retail data pipeline.

This script handles data transformation:
1. Reads raw data from raw storage
2. Cleans and transforms the data
3. Saves processed data
"""

from pathlib import Path

from etl.core.config import get_settings
from etl.core.pipeline import ProcessedLayer


class EMIRetailTransformer(ProcessedLayer):
    """Data transformer for EMI Retail: Transform raw data to processed."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Transform raw data to processed format.

        Args:
            input_path: Path to raw CSV file
            output_path: Path to save processed CSV file
        """
        print(f"\n{'='*80}")
        print("EMI RETAIL: Transform Raw to Processed")
        print(f"{'='*80}")

        # Step 1: Load raw data
        print("\n[1/3] Loading raw data...")
        print(f"      Input: {input_path}")
        df = self.read_csv(input_path, skiprows=12)  # Skip EMI metadata rows
        print(f"      ✓ Loaded {len(df)} rows, {len(df.columns)} columns")

        # Display sample
        print("\n      Sample raw data (first 3 rows):")
        print(df.head(3).to_string(index=False))

        # Step 2: Data cleaning and transformation
        print("\n[2/3] Applying transformations...")

        # Remove exact duplicates if any
        initial_rows = len(df)
        df = df.drop_duplicates()
        if initial_rows > len(df):
            print(f"      - Removed {initial_rows - len(df)} duplicate rows")
        else:
            print("      - No duplicates found")

        # Standardize column names
        df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace("-", "_")
        print(f"      - Standardized {len(df.columns)} column names")

        # Report missing values
        missing_counts = df.isnull().sum()
        if missing_counts.sum() > 0:
            print(f"      - Found {missing_counts.sum()} missing values")
            print("\n      Missing values by column:")
            for col, count in missing_counts[missing_counts > 0].items():
                print(f"        {col}: {count}")
        else:
            print("      - No missing values")

        # Step 3: Save processed data
        print("\n[3/3] Saving processed data...")
        print(f"      Output: {output_path}")
        self.write_csv(df, output_path)

        print(f"\n{'='*80}")
        print(f"✓ Transformation complete: {output_path}")
        print(f"{'='*80}\n")


def main():
    """Main function to run the transform pipeline."""
    settings = get_settings()

    # Define input (raw) and output (processed) paths
    input_path = (
        settings.raw_dir / "demo_emi_retail" / "emi_retail_20250801_20250831.csv"
    )
    output_path = settings.processed_dir / "demo_emi_retail" / "emi_retail_cleaned.csv"

    # Check if raw data exists
    if not input_path.exists():
        print(f"\n✗ Raw data not found: {input_path}")
        print("   Please run extract.py first to fetch raw data from API")
        return

    # Create transformer
    transformer = EMIRetailTransformer()

    # Run the transformation process
    try:
        transformer.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Transformation failed: {e}")
        raise


if __name__ == "__main__":
    main()
