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
        print("\n[2/5] Calculating solar capacity installed BY Sub-Category")
        solar_df1 = (
            df.loc[df["Fuel type"].isin(["Solar", "Solar (with battery)"])]
            .groupby(["Year", "Month", "Region", "Sub-Category"], as_index=False)[
                "Total capacity installed (MW)"
            ]
            .sum()
            .rename(columns={"Total capacity installed (MW)": "_07_P1_Sol"})
        )
        print(f"      ✓ Aggregated {len(solar_df1)} grouped rows")

        # Add metadata columns
        solar_df1 = solar_df1.assign(**{"Metric Group": "Energy", "Category": "Solar"})

        # Step 3: Calculate analytics
        print("\n[3/5] Calculating solar capacity installed ACROSS Sub-Category")
        solar_df2 = (
            df.loc[df["Fuel type"].isin(["Solar", "Solar (with battery)"])]
            .groupby(["Year", "Month", "Region"], as_index=False)[
                "Total capacity installed (MW)"
            ]
            .sum()
            .rename(columns={"Total capacity installed (MW)": "_07_P1_Sol"})
        )
        print(f"      ✓ Aggregated {len(solar_df2)} grouped rows")

        # Add metadata columns
        solar_df2 = solar_df2.assign(
            **{"Metric Group": "Energy", "Category": "Solar", "Sub-Category": "Total"}
        )

        # Step 4: Join datasets
        print("\n[4/5] Combining BY and ACROSS dataset")
        out_df = solar_df1._append(solar_df2)
        print(f"      ✓ Calculated {len(out_df)} battery penetration records")
        print("      ✓ Provide percentages and counts")

        # Step 3: Save analytics
        print("\n[3/3] Saving metric...")
        self.write_csv(out_df, output_path)

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
