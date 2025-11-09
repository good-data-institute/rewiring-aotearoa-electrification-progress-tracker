"""Analytics: MW of solar installed.

This script creates analytics-ready aggregated data showing
monthly MW of solar installed by region and sub-category.
"""

from pathlib import Path

from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer


class Processor_07Sol(MetricsLayer):
    """Calculate MW of solar installed."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Aggregate monthly MW of solar installed by region and sub-category.

        Args:
            input_path: Path to processed CSV
            output_path: Path to save analytics CSV
        """
        print(f"\n{'=' * 80}")
        print("EMI BATTERY AND SOLAR: 07_P1_Sol")
        print(f"{'=' * 80}")

        # Step 1: Load processed data
        print("\n[1/3] Loading processed data...")
        df = self.read_csv(input_path)
        print(f"      ✓ Loaded {len(df)} rows")

        # Step 2: Calculate analytics
        print("\n[2/3] Calculating solar capacity installed...")
        solar_df = (
            df.loc[df["Fuel type"].isin(["Solar", "Solar (with battery)"])]
            .groupby(["Year", "Month", "Region", "Sub-Category"], as_index=False)[
                "Total capacity installed (MW)"
            ]
            .sum()
            .rename(columns={"Total capacity installed (MW)": "_07_P1_Sol"})
        )
        print(f"      ✓ Aggregated {len(solar_df)} grouped rows")

        # Add metadata columns
        solar_df = solar_df.assign(**{"Metric Group": "Energy", "Category": "Solar"})

        # Step 3: Save analytics
        print("\n[3/3] Saving metric...")
        self.write_csv(solar_df, output_path)

        print(f"\n✓ Analytics complete: {len(solar_df)} rows saved")
        print(f"  Years covered: {solar_df['Year'].min()} - {solar_df['Year'].max()}")
        print(f"  Regions: {', '.join(sorted(solar_df['Region'].unique()))}")


def main():
    """Main function to run the analytics pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = (
        settings.processed_dir / "emi_battery_solar" / "emi_battery_solar_cleaned.csv"
    )
    output_path = settings.metrics_dir / "emi_battery_solar" / "_07_P1_Sol.csv"

    # Create analytics processor
    processor = Processor_07Sol()

    # Run the analytics process
    try:
        processor.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Metric calculation failed: {e}")
        raise


if __name__ == "__main__":
    main()
