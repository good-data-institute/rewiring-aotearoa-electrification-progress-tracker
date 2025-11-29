"""Analytics: EECA Energy Consumption of Fossil Fuel Boilers.

This script creates analytics-ready aggregated data showing
energy consumption by year and sector (sub-category).
Converts energy values from terajoules to MWh.
"""

from pathlib import Path

from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer


class EECAEnergyBoilersAnalytics(MetricsLayer):
    """Analytics processor for energy consumption from Fossil Fuel Boilers."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Create energy consumption from Fossil Fuel Boilers.

        Aggregates energy consumption by Year and Sub-Category (sector),
        then converts from terajoules to MWh.

        Args:
            input_path: Path to processed EECA energy consumption CSV
            output_path: Path to save analytics CSV
        """
        print(f"\n{'=' * 80}")
        print("EECA FOSSIL FUEL BOILER ENERGY: Analytics")
        print(f"{'=' * 80}")

        # Step 1: Load processed data
        print("\n[1/3] Loading processed data...")
        df = self.read_csv(input_path)
        print(f"      Loaded {len(df)} rows from {input_path.name}")

        # Step 2: Filter to Fossil Fuel Boilers
        print("\n[2/6] Filter to Fossil Fuel Boilers")
        filtered = df[(df["FossilFuelFlag"] == 1) & (df["BoilerFlag"] == 1)]
        filtered = df.drop(columns=["FossilFuelFlag", "BoilerFlag"])

        # Step 3: Calculate analytics
        print("\n[3/6] Aggregating energy consumption by sector")

        # Group and summarise
        grouped1 = filtered.groupby(["Year", "Sub-Category"], as_index=False)[
            "energyValue"
        ].sum()
        print(
            f"      - Aggregated to {len(grouped1)} rows "
            f"({df['Year'].nunique()} years × {df['Sub-Category'].nunique()} sectors)"
        )

        # Step 4: Calculate analytics
        print("\n[4/6] Aggregating energy consumption year")

        # Group and summarise
        grouped2 = df.groupby(["Year"], as_index=False)["energyValue"].sum()
        grouped2 = grouped2.assign(**{"Sub-Category": "Total"})
        print(
            f"      - Aggregated to {len(grouped2)} rows ({df['Year'].nunique()} years)"
        )

        # Step 5: Join datasets
        print("\n[5/6] Add a Total Category to Sector")
        out_df = grouped1._append(grouped2)

        # Add metadata
        out_df = out_df.assign(
            **{
                "Metric Group": "Grid",
                "Month": "Total",
                "Region": "Total",
                "Category": "Total",
            }
        )

        # Convert to MWh instead of Terajoules
        out_df["_11_P1_EnergyFF"] = out_df["energyValue"] * (1 / 0.036)
        out_df = out_df.drop(columns=["energyValue"])
        print("      - Converted from terajoules to MWh using factor (1 / 0.036)")
        print(f"      - Total energy: {out_df['_11_P1_EnergyFF'].sum():,.0f} MWh")

        # Step 5: Save analytics
        print("\n[6/6] Saving analytics...")
        self.write_csv(out_df, output_path)

        print(f"\n✓ Analytics complete: {len(out_df)} rows saved")
        print(f"  Years covered: {out_df['Year'].min()} - {out_df['Year'].max()}")
        print(f"  Sectors: {out_df['Sub-Category'].unique()}")


def main():
    """Main function to run the analytics pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = settings.processed_dir / "eeca" / "eeca_energy_consumption_cleaned.csv"
    output_path = settings.metrics_dir / "eeca" / "eeca_boilerenergy.csv"

    # Create analytics processor
    processor = EECAEnergyBoilersAnalytics()

    # Run the analytics process
    try:
        processor.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Analytics failed: {e}")
        raise


if __name__ == "__main__":
    main()
