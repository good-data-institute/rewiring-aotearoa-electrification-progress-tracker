"""Analytics: MW of batteries installed.

This script creates analytics-ready aggregated data showing
monthly MW of batteries installed by region and Sub_Category.
"""

from pathlib import Path

from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer


class Processor_08Batt(MetricsLayer):
    """Calculate MW of standalone battery capacity installed."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Aggregate monthly MW of batteries installed by region and Sub_Category.

        Args:
            input_path: Path to processed CSV
            output_path: Path to save analytics CSV
        """
        print(f"\n{'=' * 80}")
        print("EMI BATTERY AND SOLAR: 08_P1_Batt")
        print(f"{'=' * 80}")

        print("\n[1/5] Loading processed data...")
        df = self.read_csv(input_path)
        print(f"      ✓ Loaded {len(df)} rows")

        # Step 3: Calculate analytics BY Sub_Category
        print("\n[2/5] Calculating battery capacity installed BY Sub_Category")
        batt_df1 = (
            df.loc[df["Fuel type"] == "Battery (standalone)"]
            .groupby(["Year", "Month", "Region", "Sub_Category"], as_index=False)[
                "Total capacity installed (MW)"
            ]
            .sum()
            .rename(columns={"Total capacity installed (MW)": "_08_P1_Batt"})
        )
        print(f"      ✓ Aggregated {len(batt_df1)} grouped rows")

        # Add metadata columns
        batt_df1 = batt_df1.assign(**{"Metric_Group": "Energy", "Category": "Solar"})

        # Step 3: Calculate analytics ACROSS Sub_Category
        print("\n[3/5] Calculating battery capacity installed ACROSS Sub_Category")
        batt_df2 = (
            df.loc[df["Fuel type"] == "Battery (standalone)"]
            .groupby(["Year", "Month", "Region"], as_index=False)[
                "Total capacity installed (MW)"
            ]
            .sum()
            .rename(columns={"Total capacity installed (MW)": "_08_P1_Batt"})
        )
        print(f"      ✓ Aggregated {len(batt_df2)} grouped rows")

        # Add metadata columns
        batt_df2 = batt_df2.assign(
            **{"Metric_Group": "Solar", "Category": "Total", "Sub_Category": "Total"}
        )

        # Step 4: Join datasets
        print("\n[4/5] Combining BY and ACROSS dataset")
        out_df = batt_df1._append(batt_df2)
        print(f"      ✓ Calculated {len(out_df)} battery penetration records")
        print("      ✓ Provide percentages and counts")

        # Step 5: Save analytics
        print("\n[5/5] Saving metric...")
        self.write_csv(out_df, output_path)

        print(f"\n✓ Analytics complete: {len(out_df)} rows saved")
        print(f"  Years covered: {out_df['Year'].min()} - {out_df['Year'].max()}")
        print(f"  Regions: {', '.join(sorted(out_df['Region'].unique()))}")
        print(f"  Sub-Categories: {', '.join(sorted(out_df['Sub_Category'].unique()))}")


def main():
    """Main function to run the analytics pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = (
        settings.processed_dir / "emi_battery_solar" / "emi_battery_solar_cleaned.csv"
    )
    output_path = settings.metrics_dir / "emi_battery_solar" / "_08_P1_Batt.csv"

    # Create analytics processor
    processor = Processor_08Batt()

    # Run the analytics process
    try:
        processor.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Metric calculation failed: {e}")
        raise


if __name__ == "__main__":
    main()
