"""Transform: EECA Energy Consumption data pipeline.

This script handles data transformation:
1. Reads raw Excel data from raw storage
2. Cleans and transforms the data
3. Saves processed data as CSV
"""

from io import BytesIO
from pathlib import Path

import pandas as pd

from etl.apis.eeca import EECAAPI
from etl.core.config import get_settings
from etl.core.pipeline import ProcessedLayer


class EECAEnergyConsumptionTransformer(ProcessedLayer):
    """Data transformer for EECA Energy Consumption: Transform raw data to processed."""

    def __init__(
        self,
        year_from: int = None,
        year_to: int = None,
    ):
        """Initialize transformer with optional date range filters.

        Args:
            year_from: Start year for filtering (optional, applied during processing)
            year_to: End year for filtering (optional, applied during processing)
        """
        super().__init__()
        self.api = EECAAPI()
        self.year_from = year_from
        self.year_to = year_to

    def process(self, input_path: Path, output_path: Path) -> None:
        """Transform raw Excel data to processed CSV format.

        Args:
            input_path: Path to raw Excel file
            output_path: Path to save processed CSV file
        """
        print(f"\n{'='*80}")
        print("EECA ENERGY CONSUMPTION: Transform Raw to Processed")
        print(f"{'='*80}")

        # Step 1: Load raw data
        print("\n[1/3] Loading raw Excel data...")
        print(f"      Input: {input_path}")

        with open(input_path, "rb") as f:
            excel_data = f.read()

        df = pd.read_excel(BytesIO(excel_data), sheet_name=self.api.params.sheet_name)
        print(f"      ✓ Loaded {len(df)} rows, {len(df.columns)} columns")

        # Display sample
        print("\n      Sample raw data (first 3 rows):")
        print(df.head(3).to_string(index=False))

        # Step 2: Data cleaning and transformation
        print("\n[2/3] Applying transformations:")

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

        # Reassign fishing to Commercial in Sub-Categories
        df["Sub-Category"] = df["Sub-Category"].replace(
            {"Agriculture, Forestry and Fishing": "Commercial"}
        )
        print("      - Reassigned fishing group to commercial Sub-Category")

        # Remove rows where energyValue is missing
        initial_rows = len(df)
        df = df.dropna(subset=["energyValue"])
        if initial_rows > len(df):
            print(
                f"      - Removed {initial_rows - len(df)} rows with missing energyValue"
            )
        else:
            print("      - No missing energyValue values found")

        # Split the Yearly numbers by month - using an approximate season split
        # Define months and seasonal weights (example: more energy in winter)
        df_months = pd.DataFrame(
            {
                "Month": range(1, 13),
                # Rough pattern for NZ: winter (Jun–Aug) highest, summer (Dec–Feb) lowest
                "season_weight": [
                    0.7,
                    0.8,
                    0.9,
                    1.0,
                    1.1,
                    1.2,
                    1.3,
                    1.2,
                    1.1,
                    1.0,
                    0.9,
                    0.8,
                ],
            }
        )
        # Normalise weights so they sum to 12 (so totals are preserved)
        df_months["season_weight"] = df_months["season_weight"] * (
            1 / df_months["season_weight"].sum()
        )

        # Cross join years × months
        energy_count_before = df.energyValue.sum()
        df = (
            df.assign(key=1)
            .merge(df_months.assign(key=1), on="key")
            .drop("key", axis=1)
        )

        # Apply seasonal weights
        df["energyValue"] = df["energyValue"] * df["season_weight"]
        df.drop(columns=["season_weight"], inplace=True)
        print(
            "      - Added Month column by spitting yearly data using seasonal approximation"
        )
        print(
            f"      - Total Energy values match: {df.energyValue.sum() == energy_count_before}"
        )

        # Step 3: Save processed data
        print("\n[3/3] Saving processed data...")
        print(f"      Output: {output_path}")
        self.write_csv(df, output_path)

        print(f"\n{'='*80}")
        print(f"✓ Transformation complete: {len(df)} rows saved")
        print(f"  Years covered: {df['Year'].min()} - {df['Year'].max()}")
        print(f"  Categories: {', '.join(sorted(df['Category'].unique()))}")
        print(f"{'='*80}\n")


def main():
    """Main function to run the transform pipeline."""
    settings = get_settings()

    # Define input (raw) and output (processed) paths
    input_path = settings.raw_dir / "eeca" / "eeca_energy_consumption_raw.xlsx"
    output_path = (
        settings.processed_dir / "eeca" / "eeca_energy_consumption_cleaned.csv"
    )

    # Check if raw data exists
    if not input_path.exists():
        print(f"\n✗ Raw data not found: {input_path}")
        print("   Please run extract.py first to fetch raw data from API")
        return

    # Create transformer with optional date range
    transformer = EECAEnergyConsumptionTransformer(
        year_from=2017,  # Optional: filter from this year
        year_to=2023,  # Optional: filter to this year
    )

    # Run the transformation process
    try:
        transformer.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Transformation failed: {e}")
        raise


if __name__ == "__main__":
    main()
