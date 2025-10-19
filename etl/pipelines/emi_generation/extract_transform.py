"""Extract and Transform: EMI Electricity Generation data pipeline.

This script handles the complete data processing:
1. Extracts raw data from EMI Azure Blob Storage (multiple CSV files)
2. Cleans and transforms the data with POC-to-Region concordance
3. Saves processed data as CSV
"""

from io import BytesIO
from pathlib import Path

import pandas as pd

from etl.apis.emi import EMIGenerationAPI
from etl.core.config import get_settings
from etl.core.pipeline import ProcessedLayer


class EMIGenerationProcessor(ProcessedLayer):
    """Data processor for EMI Generation: Extract from Azure Blob + Transform."""

    def __init__(
        self,
        year_from: int = 2020,
        year_to: int = 2025,
    ):
        """Initialize processor with date range parameters.

        Args:
            year_from: Start year for data extraction
            year_to: End year for data extraction
        """
        super().__init__()
        self.api = EMIGenerationAPI(year_from=year_from, year_to=year_to)

    def process(self, input_path: Path, output_path: Path) -> None:
        """Extract from Azure Blob Storage and transform generation data.

        Args:
            input_path: Not used (data comes from Azure Blob)
            output_path: Path to save processed CSV file
        """
        print(f"\n{'='*80}")
        print("EMI ELECTRICITY GENERATION: Extract & Transform")
        print(f"{'='*80}")

        # Step 1: Extract from Azure Blob Storage
        print("\n[1/5] Extracting data from EMI Azure Blob Storage...")
        print(
            f"      Year range: {self.api.params.year_from}-{self.api.params.year_to}"
        )

        csv_files = self.api.fetch_generation_data()

        # Step 2: Load and concatenate CSV files
        print("\n[2/5] Loading and concatenating CSV files...")
        dfs = []
        for blob_name, data_stream in csv_files:
            # Read CSV as string to preserve schema
            df_chunk = pd.read_csv(data_stream, dtype=str)
            dfs.append(df_chunk)
            print(f"      - Loaded {len(df_chunk)} rows from {Path(blob_name).name}")

        df = pd.concat(dfs, ignore_index=True)
        print(f"      ✓ Combined {len(df)} total rows from {len(dfs)} files")

        # Step 3: Load concordance data
        print("\n[3/5] Loading POC to Region concordance...")
        concordance_data = self.api.fetch_concordance()
        concord = (
            pd.read_csv(BytesIO(concordance_data), skiprows=6)
            .query("`Current flag` == 1")
            .rename(
                columns={"POC code": "POC_Code", "Network reporting region": "Region"}
            )[["POC_Code", "Region"]]
            .drop_duplicates()
        )

        # Clean region names - remove power company names in parentheses
        concord["Region"] = (
            concord["Region"].str.replace(r"\s*\(.*?\)", "", regex=True).str.strip()
        )
        print(f"      Loaded {len(concord)} POC to Region mappings")

        # Step 4: Data cleaning and transformation
        print("\n[4/5] Applying transformations:")

        # Join regions
        df = df.merge(concord, on="POC_Code", how="left")
        df["Region"] = df["Region"].fillna("Unknown")
        print(
            f"      - Joined with regional concordance, {df['Region'].nunique()} regions found"
        )

        # Convert trading date and extract year/month
        df["Trading_Date"] = pd.to_datetime(df["Trading_Date"], errors="coerce")
        df["Year"] = df["Trading_Date"].dt.year
        df["Month"] = df["Trading_Date"].dt.month
        print("      - Extracted year and month from Trading_Date")

        # Recode renewable flag
        renewables = {
            "Hydro",
            "Wind",
            "Solar",
            "Wood",
            "Geo",
            "GEO",
            "ELE",
            "HYD",
            "SOL",
        }
        df["Type"] = df["Fuel_Code"].isin(renewables).astype(int)
        renewable_count = df["Type"].sum()
        print(
            f"      - Classified fuel types: {renewable_count:,} renewable, {len(df)-renewable_count:,} non-renewable"
        )

        # Convert numeric columns (trading periods) and sum across them
        tp_cols = [c for c in df.columns if c.startswith("TP")]
        df[tp_cols] = df[tp_cols].apply(pd.to_numeric, errors="coerce")
        df["kWh"] = df[tp_cols].sum(axis=1)
        print(f"      - Summed {len(tp_cols)} trading periods into total kWh")

        # Drop TP columns to save space
        df = df.drop(columns=tp_cols)
        print(f"      - Dropped {len(tp_cols)} trading period columns to reduce size")

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

        # Step 5: Save processed data
        print("\n[5/5] Saving processed data...")
        self.write_csv(df, output_path)

        print(f"\n✓ Processing complete: {len(df)} rows saved")
        print(
            f"  Date range: {df['Trading_Date'].min().strftime('%Y-%m-%d')} to {df['Trading_Date'].max().strftime('%Y-%m-%d')}"
        )
        print(f"  Total generation: {df['kWh'].sum():,.0f} kWh")
        print(f"  Regions: {', '.join(sorted(df['Region'].unique()))}")


def main():
    """Main function to run the extract and transform pipeline."""
    settings = get_settings()

    # Define output path
    output_path = (
        settings.processed_dir / "emi_generation" / "emi_generation_cleaned.csv"
    )

    # Create processor with year range
    # Customize these parameters as needed for different year ranges
    processor = EMIGenerationProcessor(
        year_from=2020,
        year_to=2025,
    )

    # Run the extract and transform process
    try:
        processor.process(input_path=None, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Extract & Transform failed: {e}")
        raise


if __name__ == "__main__":
    main()
