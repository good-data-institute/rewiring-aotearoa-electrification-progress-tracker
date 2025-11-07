"""Analytics: Battery penetration

This script calculates the monthly percentage of ICPs that include
batteries by region and sub-category.
"""

from pathlib import Path
import pandas as pd

from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer


class Processor_06bBattPen(MetricsLayer):
    """Calculate percentage of ICPs with batteries.

    Args:
        input_path: Path to processed CSV
        output_path: Path to save analytics CSV
    """

    def process(self, input_path: Path, output_path: Path) -> None:
        print(f"\n{'=' * 80}")
        print("EMI BATTERY AND SOLAR: 06b_P1_BattPen")
        print(f"{'=' * 80}")

        print("\n[1/3] Loading processed data...")
        df = self.read_csv(input_path)
        print(f"      ✓ Loaded {len(df)} rows")

        # Step 2: Calculate analytics
        print("\n[2/3] Calculating battery penetration (ICPs with batteries)...")

        all_icp = (
            df.groupby(["Year", "Month", "Region", "Sub-Category"], as_index=False)[
                "ICP count"
            ]
            .sum()
            .rename(columns={"ICP count": "TotalICPs"})
        )

        with_batt = (
            df.loc[
                df["Fuel type"].isin(
                    ["Solar (with battery)", "Battery (standalone)", "battery"]
                )
            ]
            .groupby(["Year", "Month", "Region", "Sub-Category"], as_index=False)[
                "ICP count"
            ]
            .sum()
            .rename(columns={"ICP count": "ICPsWithBatt"})
        )

        merged = all_icp.merge(
            with_batt, on=["Year", "Month", "Region", "Sub-Category"], how="outer"
        ).fillna(0)
        merged["_06b_P1_BattPen"] = (
            (100 * merged["ICPsWithBatt"].divide(merged["TotalICPs"]))
            .replace([float("inf"), -float("inf")], pd.NA)
            .fillna(0)
        )
        print(f"      ✓ Calculated {len(merged)} battery penetration records")

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
    output_path = settings.metrics_dir / "emi_battery_solar" / "_06b_P1_BattPen.csv"

    # Create analytics processor
    processor = Processor_06bBattPen()

    # Run the analytics process
    try:
        processor.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Metric calculation failed: {e}")
        raise


if __name__ == "__main__":
    main()
