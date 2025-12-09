"""Analytics: Waka Kotahi MVR - Number of Electric Vehicles (EVs) in use.

This script creates analytics-ready aggregated data showing
monthly electric vehicle (BEV) counts by region, category, and sub-category.

Metric ID: _01_P1_EV
"""

from pathlib import Path

import pandas as pd

from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer


class WakaKotahiEVCountAnalytics(MetricsLayer):
    """Analytics processor for EV count aggregation."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Create EV count analytics aggregated by region, category, and time.

        Args:
            input_path: Path to processed MVR Parquet file
            output_path: Path to save analytics CSV
        """
        print(f"\n{'=' * 80}")
        print("WAKA KOTAHI MVR: EV Count Analytics (_01_P1_EV)")
        print(f"{'=' * 80}")

        # Step 1: Load processed data
        print("\n[1/3] Loading processed data...")
        df = pd.read_parquet(input_path)
        print(f"      Loaded {len(df):,} rows from {input_path.name}")

        # Step 2: Calculate analytics
        print("\n[2/3] Aggregating EV counts by region, category, and sub-category...")

        # Filter for BEVs only
        df_bev = df[df["Fuel_Type"] == "BEV"].copy()
        print(f"      - Filtered to {len(df_bev):,} BEV records")

        # Define the category/sub-category combinations we want
        metrics_to_generate = [
            ("Private", "Light Passenger Vehicle"),
            ("Commercial", "Light Passenger Vehicle"),
            ("Private", "Bus"),
            ("Commercial", "Bus"),
            ("Private", "Light Commercial Vehicle"),
            ("Commercial", "Light Commercial Vehicle"),
        ]

        all_results = []

        for category, sub_category in metrics_to_generate:
            # Filter data
            df_filtered = df_bev[
                (df_bev["Category"] == category)
                & (df_bev["Sub_Category"] == sub_category)
            ].copy()

            if len(df_filtered) == 0:
                print(f"      - No data for {category} - {sub_category}, skipping")
                continue

            # Group and count
            grouped = df_filtered.groupby(
                ["Year", "Month", "Region"], as_index=False
            ).agg(_01_P1_EV=("OBJECTID", "count"))

            # Add metadata
            grouped["Metric_Group"] = "Transport"
            grouped["Category"] = category
            grouped["Sub_Category"] = sub_category
            grouped["Fuel_Type"] = "BEV"

            all_results.append(grouped)
            print(
                f"      - {category} {sub_category}: {len(grouped):,} rows, "
                f"{grouped['_01_P1_EV'].sum():,.0f} total EVs"
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
                "_01_P1_EV",
            ]
        ]

        # Step 3: Save analytics
        print("\n[3/3] Saving analytics...")
        self.write_csv(analytics_df, output_path)

        print(f"\n✓ Analytics complete: {len(analytics_df):,} rows saved")
        print(
            f"  Total EVs across all categories: {analytics_df['_01_P1_EV'].sum():,.0f}"
        )
        print(
            f"  Years covered: {analytics_df['Year'].min()} - {analytics_df['Year'].max()}"
        )
        print(f"  Categories: {analytics_df['Category'].nunique()}")
        print(f"  Sub-categories: {analytics_df['Sub_Category'].nunique()}")


def main():
    """Main function to run the analytics pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = settings.processed_dir / "waka_kotahi_mvr" / "mvr_processed.parquet"
    output_path = settings.metrics_dir / "waka_kotahi_mvr" / "01_P1_EV_analytics.csv"

    # Create analytics processor
    processor = WakaKotahiEVCountAnalytics()

    # Run the analytics process
    try:
        processor.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Analytics failed: {e}")
        raise


if __name__ == "__main__":
    main()
