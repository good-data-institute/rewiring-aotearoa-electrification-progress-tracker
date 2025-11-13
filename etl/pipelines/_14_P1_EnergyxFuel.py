"""Analytics: EECA Energy Consumption by Fuel Type.

This script creates analytics-ready aggregated data showing
energy consumption by year, fuel type (category), and sector (sub-category).
Converts energy values from terajoules to MWh.
"""

from pathlib import Path

from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer


class EECAEnergyByFuelAnalytics(MetricsLayer):
    """Analytics processor for energy consumption by fuel type."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Create energy consumption by fuel type analytics.

        Aggregates energy consumption by Year, Category (fuel type),
        and Sub-Category (sector), then converts from terajoules to MWh.

        Args:
            input_path: Path to processed EECA energy consumption CSV
            output_path: Path to save analytics CSV
        """
        print(f"\n{'='*80}")
        print("EECA ENERGY BY FUEL TYPE: Analytics")
        print(f"{'='*80}")

        # Step 1: Load processed data
        print("\n[1/3] Loading processed data...")
        df = self.read_csv(input_path)
        print(f"      Loaded {len(df)} rows from {input_path.name}")

        # Step 2: Calculate analytics
        print("\n[2/5] Aggregating energy consumption by fuel type and sector")

        # Group and summarise
        grouped1 = df.groupby(["Year", "Category", "Sub-Category"], as_index=False)[
            "energyValue"
        ].sum()
        print(
            f"      - Aggregated to {len(grouped1)} rows "
            f"({df['Year'].nunique()} years × {df['Category'].nunique()} fuel types × {df['Sub-Category'].nunique()} sectors)"
        )

        # Step 3: Calculate analytics
        print("\n[3/5] Aggregating energy consumption by fuel type")

        # Group and summarise
        grouped2 = df.groupby(["Year", "Category"], as_index=False)["energyValue"].sum()
        grouped2 = grouped2.assign(**{"Sub-Category": "Total"})
        print(
            f"      - Aggregated to {len(grouped2)} rows "
            f"({df['Year'].nunique()} years × {df['Category'].nunique()} fuel types)"
        )

        # Step 4: Join datasets
        print("\n[4/5] Add a Total Category to Sector")
        out_df = grouped1._append(grouped2)

        # Add metadata
        out_df["Metric Group"] = "Energy"

        # Convert to MWh instead of Terajoules
        out_df["_14_P1_EnergyxFuel"] = out_df["energyValue"] * (1 / 0.036)
        print("      - Converted from terajoules to MWh using factor (1 / 0.036)")
        print(f"      - Total energy: {out_df['_14_P1_EnergyxFuel'].sum():,.0f} MWh")

        # Step 5: Save analytics
        print("\n[5/5] Saving analytics...")
        self.write_csv(out_df, output_path)

        print(f"\n✓ Analytics complete: {len(out_df)} rows saved")
        print(f"  Years covered: {out_df['Year'].min()} - {out_df['Year'].max()}")
        print(f"  Fuel types: {', '.join(sorted(out_df['Category'].unique()))}")
        print(f"  Sectors: {out_df['Sub-Category'].unique()}")


def main():
    """Main function to run the analytics pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = settings.processed_dir / "eeca" / "eeca_energy_consumption_cleaned.csv"
    output_path = settings.metrics_dir / "eeca" / "eeca_energy_by_fuel.csv"

    # Create analytics processor
    processor = EECAEnergyByFuelAnalytics()

    # Run the analytics process
    try:
        processor.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Analytics failed: {e}")
        raise


if __name__ == "__main__":
    main()
