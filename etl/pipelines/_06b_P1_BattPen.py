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

        # Step 2: Calculate analytics BY Sub-Category
        print(
            "\n[2/5] Calculating battery penetration (ICPs with batteries) BY Sub-Category"
        )

        all_icp1 = (
            df.groupby(["Year", "Month", "Region", "Sub-Category"], as_index=False)[
                "ICP count"
            ]
            .sum()
            .rename(columns={"ICP count": "TotalICPs"})
        )

        with_batt1 = (
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

        merged1 = all_icp1.merge(
            with_batt1, on=["Year", "Month", "Region", "Sub-Category"], how="outer"
        ).fillna(0)
        merged1["_06b_P1_BattPen"] = (
            (100 * merged1["ICPsWithBatt"].divide(merged1["TotalICPs"]))
            .replace([float("inf"), -float("inf")], pd.NA)
            .fillna(0)
        )
        print(f"      ✓ Calculated {len(merged1)} battery penetration records")

        # Add metadata columns
        merged1 = merged1.assign(**{"Metric Group": "Energy", "Category": "Solar"})

        # Step 3: Calculate analytics BY Sub-Category
        print(
            "\n[3/5] Calculating battery penetration (ICPs with batteries) ACROSS Sub-Category"
        )

        all_icp2 = (
            df.groupby(["Year", "Month", "Region"], as_index=False)["ICP count"]
            .sum()
            .rename(columns={"ICP count": "TotalICPs"})
        )

        with_batt2 = (
            df.loc[
                df["Fuel type"].isin(
                    ["Solar (with battery)", "Battery (standalone)", "battery"]
                )
            ]
            .groupby(["Year", "Month", "Region"], as_index=False)["ICP count"]
            .sum()
            .rename(columns={"ICP count": "ICPsWithBatt"})
        )

        merged2 = all_icp2.merge(
            with_batt2, on=["Year", "Month", "Region"], how="outer"
        ).fillna(0)
        merged2["_06b_P1_BattPen"] = (
            (100 * merged2["ICPsWithBatt"].divide(merged2["TotalICPs"]))
            .replace([float("inf"), -float("inf")], pd.NA)
            .fillna(0)
        )
        print(f"      ✓ Calculated {len(merged2)} battery penetration records")

        # Add metadata columns
        merged2 = merged2.assign(
            **{"Metric Group": "Energy", "Category": "Solar", "Sub-Category": "Total"}
        )

        # Step 4: Join datasets
        print("\n[4/5] Combining BY and ACROSS dataset")
        out_df = merged1._append(merged2)
        print(f"      ✓ Calculated {len(out_df)} battery penetration records")
        print("      ✓ Provide percentages and counts")

        # Step 5: Save analytics
        print("\n[5/5] Saving metric...")
        self.write_parquet(out_df, output_path)

        print(f"\n✓ Analytics complete: {len(out_df)} rows saved")
        print(f"  Years covered: {out_df['Year'].min()} - {out_df['Year'].max()}")
        print(f"  Regions: {', '.join(sorted(out_df['Region'].unique()))}")
        print(f"  Sub-Categories: {', '.join(sorted(out_df['Sub-Category'].unique()))}")


def main():
    """Main function to run the analytics pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = (
        settings.processed_dir / "emi_battery_solar" / "emi_battery_solar_cleaned.csv"
    )
    output_path = settings.metrics_dir / "emi_battery_solar" / "_06b_P1_BattPen.parquet"

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
