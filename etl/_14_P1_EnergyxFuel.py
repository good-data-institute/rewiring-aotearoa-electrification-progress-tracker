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
        print("\n[2/3] Aggregating energy consumption by fuel type and sector...")

        # Group and summarise
        grouped = df.groupby(["Year", "Category", "Sub-Category"], as_index=False)[
            "energyValue"
        ].sum()
        print(
            f"      - Aggregated to {len(grouped)} rows "
            f"({df['Year'].nunique()} years × {df['Category'].nunique()} fuel types × {df['Sub-Category'].nunique()} sectors)"
        )

        # Convert to MWh instead of Terajoules
        grouped["_14_P1_EnergyxFuel"] = grouped["energyValue"] * (1 / 0.036)
        print("      - Converted from terajoules to MWh using factor (1 / 0.036)")
        print(f"      - Total energy: {grouped['_14_P1_EnergyxFuel'].sum():,.0f} MWh")

        # Add metadata
        grouped["Metric Group"] = "Energy"

        # Select columns
        grouped = grouped[
            [
                "Year",
                "Category",
                "Sub-Category",
                "Metric Group",
                "_14_P1_EnergyxFuel",
            ]
        ]

        # Step 3: Save analytics
        print("\n[3/3] Saving analytics...")
        self.write_csv(grouped, output_path)

        print(f"\n✓ Analytics complete: {len(grouped)} rows saved")
        print(f"  Years covered: {grouped['Year'].min()} - {grouped['Year'].max()}")
        print(f"  Fuel types: {', '.join(sorted(grouped['Category'].unique()))}")
        print(f"  Sectors: {grouped['Sub-Category'].nunique()}")


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
