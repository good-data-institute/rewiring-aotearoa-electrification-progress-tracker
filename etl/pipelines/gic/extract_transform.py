"""Extract and Transform: GIC Gas Connections data pipeline.

This script handles the complete data processing:
1. Extracts raw data from GIC Registry Statistics (Excel file)
2. Cleans and transforms the data with regional mapping
3. Saves processed data as CSV
"""

from io import BytesIO
from pathlib import Path

import pandas as pd

from etl.apis.gic import GICAPI
from etl.core.config import get_settings
from etl.core.pipeline import ProcessedLayer


class GICGasConnectionsProcessor(ProcessedLayer):
    """Data processor for GIC Gas Connections: Extract from API + Transform."""

    def __init__(
        self,
        year_from: int = None,
        year_to: int = None,
        month_from: int = None,
        month_to: int = None,
    ):
        """Initialize processor with optional date range filters.

        Args:
            year_from: Start year for filtering (optional)
            year_to: End year for filtering (optional)
            month_from: Start month for filtering (optional)
            month_to: End month for filtering (optional)
        """
        super().__init__()
        self.api = GICAPI()
        self.year_from = year_from
        self.year_to = year_to
        self.month_from = month_from
        self.month_to = month_to

    def process(self, input_path: Path, output_path: Path) -> None:
        """Extract from API and transform GIC gas connections data.

        Args:
            input_path: Not used (data comes from API)
            output_path: Path to save processed CSV file
        """
        print(f"\n{'='*80}")
        print("GIC GAS CONNECTIONS: Extract & Transform")
        print(f"{'='*80}")

        # Step 1: Extract from API
        print("\n[1/4] Extracting data from GIC Registry Statistics...")
        print(f"      URL: {self.api.params.url}")

        # Fetch Excel file
        excel_data = self.api.fetch_data()
        print("      ✓ Excel file downloaded")

        # Step 2: Load main data and concordance
        print("\n[2/4] Loading data and regional concordance...")

        # Load 'By Gas Gate' sheet
        df = pd.read_excel(BytesIO(excel_data), sheet_name=self.api.params.sheet_name)
        df = df.rename(columns={"Month": "Date"})
        # Filter out rows where Gas Gate Code is "None"
        df = df[df["Gas Gate Code"] != "None"]
        print(f"      Loaded {len(df)} rows from '{self.api.params.sheet_name}' sheet")

        # Load region concordance from 'Gate Region' sheet
        region_corr = pd.read_excel(
            BytesIO(excel_data), sheet_name=self.api.params.region_sheet_name
        ).rename(columns={"Gate Region": "Region"})
        print(
            f"      Loaded {len(region_corr)} region mappings from '{self.api.params.region_sheet_name}' sheet"
        )

        # Display sample
        print("\n      Sample data (first 3 rows):")
        print(df.head(3).to_string(index=False))

        # Step 3: Data cleaning and transformation
        print("\n[3/4] Applying transformations:")

        # Convert dates and extract year/month
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month
        print("      - Extracted year and month from Date")

        # Join with region concordance
        df = df.merge(region_corr, on="Gas Gate Code", how="left")
        df["Region"] = df["Region"].fillna("Unknown")
        print(
            f"      - Joined with regional concordance, {df['Region'].nunique()} regions found"
        )

        # Filter by date range if specified
        if self.year_from or self.year_to or self.month_from or self.month_to:
            initial_rows = len(df)
            if self.year_from:
                df = df[df["Year"] >= self.year_from]
            if self.year_to:
                df = df[df["Year"] <= self.year_to]
            if self.month_from:
                df = df[df["Month"] >= self.month_from]
            if self.month_to:
                df = df[df["Month"] <= self.month_to]
            print(f"      - Filtered by date range: {initial_rows} → {len(df)} rows")

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

        # Step 4: Save processed data
        print("\n[4/4] Saving processed data...")
        self.write_csv(df, output_path)

        print(f"\n✓ Processing complete: {len(df)} rows saved")
        print(
            f"  Date range: {df['Date'].min().strftime('%Y-%m')} to {df['Date'].max().strftime('%Y-%m')}"
        )
        print(f"  Regions: {', '.join(sorted(df['Region'].unique()))}")
        if "NEW" in df.columns:
            print(f"  Total new connections: {df['NEW'].sum():,.0f}")


def main():
    """Main function to run the extract and transform pipeline."""
    settings = get_settings()

    # Define output path
    output_path = settings.processed_dir / "gic" / "gic_gas_connections_cleaned.csv"

    # Create processor with optional date range
    # Customize these parameters as needed for different date ranges
    processor = GICGasConnectionsProcessor(
        year_from=None,  # Optional: filter from this year
        year_to=None,  # Optional: filter to this year
    )

    # Run the extract and transform process
    try:
        processor.process(input_path=None, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Extract & Transform failed: {e}")
        raise


if __name__ == "__main__":
    main()
