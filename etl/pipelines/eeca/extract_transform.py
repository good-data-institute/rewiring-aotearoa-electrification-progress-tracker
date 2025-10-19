"""Extract and Transform: EECA Energy Consumption data pipeline.

This script handles the complete data processing:
1. Extracts raw data from EECA Energy End Use Database (Excel file)
2. Cleans and transforms the data
3. Saves processed data as CSV
"""

from io import BytesIO
from pathlib import Path

import pandas as pd

from etl.apis.eeca import EECAAPI
from etl.core.config import get_settings
from etl.core.pipeline import ProcessedLayer


class EECAEnergyConsumptionProcessor(ProcessedLayer):
    """Data processor for EECA Energy Consumption: Extract from API + Transform."""

    def __init__(
        self,
        year_from: int = None,
        year_to: int = None,
    ):
        """Initialize processor with optional date range filters.

        Args:
            year_from: Start year for filtering (optional, applied during processing)
            year_to: End year for filtering (optional, applied during processing)
        """
        super().__init__()
        self.api = EECAAPI()
        self.year_from = year_from
        self.year_to = year_to

    def process(self, input_path: Path, output_path: Path) -> None:
        """Extract from API and transform EECA energy consumption data.

        Args:
            input_path: Not used (data comes from API)
            output_path: Path to save processed CSV file
        """
        print(f"\n{'='*80}")
        print("EECA ENERGY CONSUMPTION: Extract & Transform")
        print(f"{'='*80}")

        # Step 1: Extract from API
        print("\n[1/3] Extracting data from EECA Energy End Use Database...")
        print(f"      URL: {self.api.params.url}")

        # Fetch Excel file
        excel_data = self.api.fetch_data()
        print("      ✓ Excel file downloaded")

        # Step 2: Load and transform
        print("\n[2/3] Loading and transforming data...")

        # Load Excel into pandas
        df = pd.read_excel(BytesIO(excel_data), sheet_name=self.api.params.sheet_name)
        print(f"      Loaded {len(df)} rows, {len(df.columns)} columns")

        # Display sample
        print("\n      Sample data (first 3 rows):")
        print(df.head(3).to_string(index=False))

        # Data cleaning and transformation
        print("\n      Applying transformations:")

        # Standardize fuel categories
        fuel_map = {
            "Electricity": "Electricity",
            "Petrol": "Petrol",
            "Diesel": "Diesel",
            "Coal": "Coal",
            "Wood": "Wood",
        }
        df["Category"] = df["fuel"].map(fuel_map).fillna("Other")
        print(f"      - Mapped fuel types to {df['Category'].nunique()} categories")

        # Convert periodEndDate to datetime and extract year
        df["periodEndDate"] = pd.to_datetime(df["periodEndDate"], errors="coerce")
        df["Year"] = df["periodEndDate"].dt.year
        print("      - Extracted year from periodEndDate")

        # Filter by year range if specified
        if self.year_from or self.year_to:
            initial_rows = len(df)
            if self.year_from:
                df = df[df["Year"] >= self.year_from]
            if self.year_to:
                df = df[df["Year"] <= self.year_to]
            print(
                f"      - Filtered to years {self.year_from or 'start'}-{self.year_to or 'end'}: "
                f"{initial_rows} → {len(df)} rows"
            )

        # Select and rename columns
        df = df[["SectorGroup", "energyValue", "Category", "Year"]].rename(
            columns={"SectorGroup": "Sub-Category"}
        )
        print(f"      - Selected {len(df.columns)} columns")

        # Remove duplicates
        initial_rows = len(df)
        df = df.drop_duplicates()
        if initial_rows > len(df):
            print(f"      - Removed {initial_rows - len(df)} duplicate rows")
        else:
            print("      - No duplicates found")

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
        self.write_csv(df, output_path)

        print(f"\n✓ Processing complete: {len(df)} rows saved")
        print(f"  Years covered: {df['Year'].min()} - {df['Year'].max()}")
        print(f"  Categories: {', '.join(sorted(df['Category'].unique()))}")


def main():
    """Main function to run the extract and transform pipeline."""
    settings = get_settings()

    # Define output path
    output_path = (
        settings.processed_dir / "eeca" / "eeca_energy_consumption_cleaned.csv"
    )

    # Create processor with optional date range
    # Customize these parameters as needed for different date ranges
    processor = EECAEnergyConsumptionProcessor(
        year_from=2017,  # Optional: filter from this year
        year_to=2023,  # Optional: filter to this year
    )

    # Run the extract and transform process
    try:
        processor.process(input_path=None, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Extract & Transform failed: {e}")
        raise


if __name__ == "__main__":
    main()
