"""Extract and Transform: EMI Retail data pipeline.

This script handles the complete data layer (silver) processing:
1. Extracts raw data from EMI Retail API
2. Cleans and transforms the data
3. Saves to silver layer

This combines what was previously done in separate bronze and silver layers.
"""

from pathlib import Path

from etl.apis.emi_retail import EMIRetailAPI
from etl.core.config import get_settings
from etl.core.pipeline import DataLayer


class EMIRetailDataProcessor(DataLayer):
    """Data layer processor for EMI Retail: Extract from API + Transform."""

    def __init__(
        self,
        report_id: str = "GUEHMT",
        capacity: str = "All_Drilldown",
        date_from: str = "20250801",
        date_to: str = "20250831",
        region_type: str = "NZ",
        fuel_type: str = "All_Drilldown",
    ):
        """Initialize processor with API parameters.

        Args:
            report_id: EMI report ID
            capacity: Capacity filter
            date_from: Start date (YYYYMMDD)
            date_to: End date (YYYYMMDD)
            region_type: Region type filter
            fuel_type: Fuel type filter
        """
        super().__init__()
        self.api = EMIRetailAPI(
            report_id=report_id,
            Capacity=capacity,
            DateFrom=date_from,
            DateTo=date_to,
            RegionType=region_type,
            FuelType=fuel_type,
        )

    def process(self, input_path: Path, output_path: Path) -> None:
        """Extract from API and transform to silver layer.

        Args:
            input_path: Not used (data comes from API)
            output_path: Path to save silver CSV file
        """
        print(f"\n{'='*80}")
        print("EMI RETAIL: Extract & Transform to Silver Layer")
        print(f"{'='*80}")

        # Step 1: Extract from API
        print("\n[1/3] Extracting data from EMI Retail API...")
        print(f"      Parameters: {self.api.params.model_dump()}")

        # Fetch data to a temporary location
        temp_path = output_path.parent / f"temp_{output_path.name}"
        self.api.fetch_data(output_path=temp_path)
        print("      ✓ API data fetched")

        # Step 2: Load and transform
        print("\n[2/3] Transforming data...")
        df = self.read_csv(temp_path, skiprows=12)  # Skip EMI metadata rows
        print(f"      Loaded {len(df)} rows, {len(df.columns)} columns")

        # Display sample
        print("\n      Sample data (first 3 rows):")
        print(df.head(3).to_string(index=False))

        # Data cleaning and transformation
        print("\n      Applying transformations:")

        # Remove exact duplicates if any
        initial_rows = len(df)
        df = df.drop_duplicates()
        if initial_rows > len(df):
            print("      - Removed {initial_rows - len(df)} duplicate rows")
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

        # Step 3: Save to silver layer
        print("\n[3/3] Saving to silver layer...")
        self.write_csv(df, output_path)

        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()

        # Summary
        print(f"\n{'='*80}")
        print("✓ COMPLETED: Silver layer data ready")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Output: {output_path}")
        print(f"{'='*80}\n")


def main():
    """Main function to run the extract and transform pipeline."""
    settings = get_settings()

    # Define output path in silver layer
    output_path = settings.silver_dir / "emi" / "emi_retail_cleaned.csv"

    # Create processor with default parameters
    # Customize these parameters as needed for different date ranges or filters
    processor = EMIRetailDataProcessor(
        report_id="GUEHMT",
        capacity="All_Drilldown",
        date_from="20250801",
        date_to="20250831",
        region_type="NZ",
        fuel_type="All_Drilldown",
    )

    # Run the extract and transform process
    try:
        processor.process(input_path=None, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Extract & Transform failed: {e}")
        raise


if __name__ == "__main__":
    main()
