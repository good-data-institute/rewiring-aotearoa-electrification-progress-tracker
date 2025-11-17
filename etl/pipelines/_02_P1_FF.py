"""Analytics: Waka Kotahi MVR - Number of Fossil Fuel vehicles in use.

This script creates analytics-ready aggregated data showing
monthly fossil fuel vehicle counts (HEV, PHEV, FCEV, Petrol, Diesel)
by region, category, and sub-category.

Metric ID: _02_P1_FF
"""

from pathlib import Path

import pandas as pd

from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer


class WakaKotahiFossilFuelCountAnalytics(MetricsLayer):
    """Analytics processor for fossil fuel vehicle count aggregation."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Create fossil fuel vehicle count analytics by region, category, and time.

        Args:
            input_path: Path to processed MVR Parquet file
            output_path: Path to save analytics CSV
        """
        print(f"\n{'='*80}")
        print("WAKA KOTAHI MVR: Fossil Fuel Vehicle Count Analytics (_02_P1_FF)")
        print(f"{'='*80}")

        # Step 1: Load processed data
        print("\n[1/3] Loading processed data...")
        df = pd.read_parquet(input_path)
        print(f"      Loaded {len(df):,} rows from {input_path.name}")

        # Step 2: Calculate analytics
        print("\n[2/3] Aggregating fossil fuel vehicle counts...")

        # Define fuel types to track
        fossil_fuel_types = ["HEV", "PHEV", "FCEV", "Petrol", "Diesel"]

        # Define the category/sub-category combinations we want
        category_combinations = [
            ("Private", "Light Passenger Vehicle"),
            ("Commercial", "Light Passenger Vehicle"),
            ("Private", "Light Commercial Vehicle"),
            ("Commercial", "Light Commercial Vehicle"),
        ]

        all_results = []

        for fuel_type in fossil_fuel_types:
            for category, sub_category in category_combinations:
                # Filter data
                df_filtered = df[
                    (df["Fuel_Type"] == fuel_type)
                    & (df["Category"] == category)
                    & (df["Sub_Category"] == sub_category)
                ].copy()

                if len(df_filtered) == 0:
                    continue

                # Group and count
                grouped = df_filtered.groupby(
                    ["Year", "Month", "Region"], as_index=False
                ).agg(_02_P1_FF=("OBJECTID", "count"))

                # Add metadata
                grouped["Metric_Group"] = "Transport"
                grouped["Category"] = category
                grouped["Sub_Category"] = sub_category
                grouped["Fuel_Type"] = fuel_type

                all_results.append(grouped)
                print(
                    f"      - {fuel_type} / {category} / {sub_category}: "
                    f"{len(grouped):,} rows, {grouped['_02_P1_FF'].sum():,.0f} vehicles"
                )

        # Combine all results
        analytics_df = pd.concat(all_results, ignore_index=True)

        # Reorder columns
        analytics_df = analytics_df[
            [
                "Year",
                "Month",
                "Region",
                "Metric_Group",
                "Category",
                "Sub_Category",
                "Fuel_Type",
                "_02_P1_FF",
            ]
        ]

        # Step 3: Save analytics
        print("\n[3/3] Saving analytics...")
        self.write_csv(analytics_df, output_path)

        print(f"\n✓ Analytics complete: {len(analytics_df):,} rows saved")
        print(f"  Total fossil fuel vehicles: {analytics_df['_02_P1_FF'].sum():,.0f}")
        print(
            f"  Years covered: {analytics_df['Year'].min()} - {analytics_df['Year'].max()}"
        )
        print(f"  Fuel types: {', '.join(sorted(analytics_df['Fuel_Type'].unique()))}")


def main():
    """Main function to run the analytics pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = settings.processed_dir / "waka_kotahi_mvr" / "mvr_processed.parquet"
    output_path = settings.metrics_dir / "waka_kotahi_mvr" / "02_P1_FF_analytics.csv"

    # Create analytics processor
    processor = WakaKotahiFossilFuelCountAnalytics()

    # Run the analytics process
    try:
        processor.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Analytics failed: {e}")
        raise


if __name__ == "__main__":
    main()
