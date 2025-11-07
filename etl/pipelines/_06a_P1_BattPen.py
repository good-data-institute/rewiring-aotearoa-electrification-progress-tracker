"""Analytics: Battery penetration

This script calculates the monthly percentage of solar installs that include
batteries by  region and sub-category.
"""

from pathlib import Path
import pandas as pd

from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer


class Processor_06aBattPen(MetricsLayer):
    """Calculate percentage of solar installations that include batteries.

    Args:
        input_path: Path to processed CSV
        output_path: Path to save analytics CSV
    """

    def process(self, input_path: Path, output_path: Path) -> None:
        print(f"\n{'=' * 80}")
        print("EMI BATTERY AND SOLAR: 06a_P1_BattPen")
        print(f"{'=' * 80}")

        print("\n[1/3] Loading processed data...")
        df = self.read_csv(input_path)
        print(f"      ✓ Loaded {len(df)} rows")

        # Step 2: Calculate analytics
        print(
            "\n[2/3] Calculating battery penetration (solar installs with batteries)..."
        )

        all_solar = (
            df.loc[df["Fuel type"].isin(["Solar", "Solar (with battery)"])]
            .groupby(["Year", "Month", "Region", "Sub-Category"], as_index=False)[
                "ICP count - new installations"
            ]
            .sum()
            .rename(columns={"ICP count - new installations": "SolarInstalls"})
        )

        solar_with_batt = (
            df.loc[df["Fuel type"] == "Solar (with battery)"]
            .groupby(["Year", "Month", "Region", "Sub-Category"], as_index=False)[
                "ICP count - new installations"
            ]
            .sum()
            .rename(columns={"ICP count - new installations": "SolarInstallsWithBatt"})
        )

        merged = all_solar.merge(
            solar_with_batt,
            on=["Year", "Month", "Region", "Sub-Category"],
            how="outer",
        ).fillna(0)
        merged["_06a_P1_BattPen"] = (
            (100 * merged["SolarInstallsWithBatt"].divide(merged["SolarInstalls"]))
            .replace([float("inf"), -float("inf")], pd.NA)
            .fillna(0)
        )
        print(f"      ✓ Calculated {len(merged)} battery penetration records")
        print("      ✓ Provide percentages and counts")

        # Add metadata columns
        merged = merged.assign(**{"Metric Group": "Energy", "Category": "Solar"})

        # Step 3: Save analytics
        print("\n[3/3] Saving metric...")
        self.write_csv(merged, output_path)

        print(f"\n✓ Analytics complete: {len(merged)} rows saved")
        print(f"  Years covered: {merged['Year'].min()} - {merged['Year'].max()}")
        print(f"  Regions: {', '.join(sorted(merged['Region'].unique()))}")


def main():
    """Main function to run the analytics pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = (
        settings.processed_dir / "emi_battery_solar" / "emi_battery_solar_cleaned.csv"
    )
    output_path = settings.metrics_dir / "emi_battery_solar" / "_06a_P1_BattPen.csv"

    # Create analytics processor
    processor = Processor_06aBattPen()

    # Run the analytics process
    try:
        processor.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Metric calculation failed: {e}")
        raise


if __name__ == "__main__":
    main()
