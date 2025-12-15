"""Transform: EMI Battery and solar data pipeline.

This script handles data transformation:
1. Reads raw CSV files from raw storage
2. Cleans and standardises data
3. Saves processed data for downstream analytics
"""

from pathlib import Path
import json

import pandas as pd

from etl.core.config import get_settings
from etl.core.pipeline import ProcessedLayer
from etl.core.mappings import EMI_REGION_MAP


class EMIBatterySolarTransformer(ProcessedLayer):
    """Data transformer for EMI Battery and solar data: Transform raw data to processed."""

    def process(self, input_dir: Path, output_path: Path) -> None:
        print(f"\n{'=' * 80}")
        print("EMI BATTERY AND SOLAR: Transform Raw to Processed")
        print(f"{'=' * 80}")

        # Load manifest
        manifest_path = input_dir / "_manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        files = manifest.get("files", [])
        print(f"\n[1/3] Loading {len(files)} raw CSV files...")

        dfs = []
        for filename in files:
            fp = input_dir / filename
            if fp.exists():
                df = pd.read_csv(fp)
                df["Sub_Category"] = filename.split("_")[0].capitalize()
                dfs.append(df)
                print(f"      ✓ Loaded: {filename} ({len(df)} rows)")
            else:
                print(f"      ⚠ Missing file: {filename}")

        df = pd.concat(dfs, ignore_index=True).rename(
            columns={"Region name": "Location"}
        )
        print(f"      ✓ Combined total rows: {len(df)}")

        print("\n[2/3] Cleaning data...")

        # Clean region names
        df["Location"] = (
            df["Location"].str.replace(r"\s*\(.*?\)", "", regex=True).str.strip()
        )
        print("      ✓ Cleaned locations")

        # Assign Locations to Regions
        before_join = df
        df["Region"] = df["Location"].map(EMI_REGION_MAP).fillna("Unknown")
        print("      ✓ Assigned Locations to Regions")
        print(f"      ✓ Rows before join: {len(before_join)}, rows after: {len(df)}")

        # Convert and extract date components
        df["Date"] = pd.to_datetime(df["Month end"], errors="coerce", dayfirst=True)
        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month
        df = df.drop(
            ["Month end", "Date", "Avg. capacity - new installations (kW)"], axis=1
        )
        print("      ✓ Extracted Year/Month")

        # Drop NAs
        df = df.dropna(subset=["Fuel type"])
        print("      ✓ Dropped rows with missing Fuel type")

        # Report missing values
        missing_counts = df.isnull().sum()
        if missing_counts.sum() > 0:
            print(f"      - Found {missing_counts.sum()} missing values")
            print("\n      Missing values by column:")
            for col, count in missing_counts[missing_counts > 0].items():
                print(f"        {col}: {count}")
        else:
            print("      - No missing values")

        print("\n[3/3] Saving processed data...")
        self.write_csv(df, output_path)

        print(f"\n✓ Transformation complete: {len(df)} rows saved")
        print(f"  Years: {df['Year'].min()} - {df['Year'].max()}")
        print(f"{'=' * 80}\n")


def main():
    """Main function to run the transform pipeline."""
    settings = get_settings()

    # Define input (raw) and output (processed) paths
    input_dir = settings.raw_dir / "emi_battery_solar"
    output_path = (
        settings.processed_dir / "emi_battery_solar" / "emi_battery_solar_cleaned.csv"
    )

    # Check if raw data exists
    if not input_dir.exists():
        print(f"\n✗ Raw data directory not found: {input_dir}")
        print("   Please run extract.py first to fetch raw data")
        return

    # Create transformer
    transformer = EMIBatterySolarTransformer()

    # Run the transformation process
    try:
        transformer.process(input_dir=input_dir, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Transformation failed: {e}")
        raise


if __name__ == "__main__":
    main()
