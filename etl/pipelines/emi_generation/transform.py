"""Transform: EMI Electricity Generation data pipeline.

This script handles data transformation:
1. Reads raw CSV files from raw storage (multiple files)
2. Cleans and transforms the data with POC-to-Region concordance
3. Saves processed data as single consolidated CSV
"""

from io import BytesIO
from pathlib import Path
import json

import pandas as pd

from etl.core.config import get_settings
from etl.core.pipeline import ProcessedLayer
from etl.core.mappings import EMI_REGION_MAP


class EMIGenerationTransformer(ProcessedLayer):
    """Data transformer for EMI Generation: Transform raw data to processed."""

    def process(self, input_dir: Path, output_path: Path) -> None:
        """Transform raw CSV files to processed format.

        Args:
            input_dir: Directory containing raw CSV files
            output_path: Path to save processed CSV file
        """
        print(f"\n{'='*80}")
        print("EMI ELECTRICITY GENERATION: Transform Raw to Processed")
        print(f"{'='*80}")

        # Step 1: Load manifest and raw data files
        print("\n[1/5] Loading raw data files...")
        print(f"      Input directory: {input_dir}")

        manifest_path = input_dir / "_manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        file_list = manifest.get("files", [])
        print(f"      ✓ Found {len(file_list)} files in manifest")

        # Step 2: Load and concatenate CSV files
        print("\n[2/5] Loading and concatenating CSV files...")
        dfs = []
        for filename in file_list:
            file_path = input_dir / filename
            if file_path.exists():
                # Read CSV as string to preserve schema
                df_chunk = pd.read_csv(file_path, dtype=str)
                dfs.append(df_chunk)
                print(f"      - Loaded {len(df_chunk)} rows from {filename}")
            else:
                print(f"      ⚠ Warning: File not found: {filename}")

        df = pd.concat(dfs, ignore_index=True)
        print(f"      ✓ Combined {len(df)} total rows from {len(dfs)} files")

        # Step 3: Load concordance data
        print("\n[3/5] Loading POC to Region concordance...")
        concordance_path = input_dir / "poc_region_concordance.csv"

        if not concordance_path.exists():
            raise FileNotFoundError(f"Concordance file not found: {concordance_path}")

        with open(concordance_path, "rb") as f:
            concordance_data = f.read()

        concord = (
            pd.read_csv(BytesIO(concordance_data), skiprows=6)
            .query("`Current flag` == 1")
            .rename(
                columns={"POC code": "POC_Code", "Network reporting region": "Location"}
            )[["POC_Code", "Location"]]
            .drop_duplicates()
        )

        # Clean region names - remove power company names in parentheses
        concord["Location"] = (
            concord["Location"].str.replace(r"\s*\(.*?\)", "", regex=True).str.strip()
        )
        print(f"      ✓ Loaded {len(concord)} POC to Location mappings")

        # Assign Locations to Regions
        before_join = df
        concord["Region"] = concord["Location"].map(EMI_REGION_MAP).fillna("Unknown")
        print("      ✓ Assigned Locations to Regions")
        print(f"      ✓ Rows before join: {len(before_join)}, rows after: {len(df)}")

        # Step 4: Data cleaning and transformation
        print("\n[4/5] Applying transformations:")

        # Join regions
        df = df.merge(concord, on="POC_Code", how="left")
        df["Region"] = df["Region"].fillna("Unknown")
        df["Location"] = df["Location"].fillna("Unknown")
        print(
            f"      - Joined with Location concordance, {df['Region'].nunique()} regions and {df['Location'].nunique()} found"
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
        print(f"      Output: {output_path}")
        self.write_csv(df, output_path)

        print(f"\n{'='*80}")
        print(f"✓ Transformation complete: {len(df)} rows saved")
        print(
            f"  Date range: {df['Trading_Date'].min().strftime('%Y-%m-%d')} to {df['Trading_Date'].max().strftime('%Y-%m-%d')}"
        )
        print(f"  Total generation: {df['kWh'].sum():,.0f} kWh")
        print(f"  Regions: {', '.join(sorted(df['Region'].unique()))}")
        print(f"{'='*80}\n")


def main():
    """Main function to run the transform pipeline."""
    settings = get_settings()

    # Define input (raw) and output (processed) paths
    input_dir = settings.raw_dir / "emi_generation"
    output_path = (
        settings.processed_dir / "emi_generation" / "emi_generation_cleaned.csv"
    )

    # Check if raw data exists
    if not input_dir.exists():
        print(f"\n✗ Raw data directory not found: {input_dir}")
        print("   Please run extract.py first to fetch raw data from Azure Blob")
        return

    # Create transformer
    transformer = EMIGenerationTransformer()

    # Run the transformation process
    try:
        transformer.process(input_dir=input_dir, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Transformation failed: {e}")
        raise


if __name__ == "__main__":
    main()
