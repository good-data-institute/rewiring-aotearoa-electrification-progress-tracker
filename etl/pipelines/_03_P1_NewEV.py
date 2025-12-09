"""Analytics: Waka Kotahi MVR - Number of New EVs purchased.

This script creates analytics-ready aggregated data showing
monthly new (not used) electric vehicle (BEV) purchase counts
by region, category, and sub-category.

Metric ID: _03_P1_NewEV
"""

from pathlib import Path

import pandas as pd

from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer


class WakaKotahiNewEVCountAnalytics(MetricsLayer):
    """Analytics processor for new EV purchase count aggregation."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Create new EV purchase count analytics by region, category, and time.

        Args:
            input_path: Path to processed MVR Parquet file
            output_path: Path to save analytics CSV
        """
        print(f"\n{'=' * 80}")
        print("WAKA KOTAHI MVR: New EV Purchase Count Analytics (_03_P1_NewEV)")
        print(f"{'=' * 80}")

        # Step 1: Load processed data
        print("\n[1/3] Loading processed data...")
        df = pd.read_parquet(input_path)
        print(f"      Loaded {len(df):,} rows from {input_path.name}")

        # Step 2: Calculate analytics
        print("\n[2/3] Aggregating new EV purchase counts...")

        # Filter for NEW BEVs only
        df_new_bev = df[(df["Fuel_Type"] == "BEV") & (df["Condition"] == "NEW")].copy()
        print(f"      - Filtered to {len(df_new_bev):,} new BEV records")

        # Define the category/sub-category combinations we want
        category_combinations = [
            ("Private", "Light Passenger Vehicle"),
            ("Commercial", "Light Passenger Vehicle"),
            ("Private", "Light Commercial Vehicle"),
            ("Commercial", "Light Commercial Vehicle"),
        ]

        all_results = []

        for category, sub_category in category_combinations:
            # Filter data
            df_filtered = df_new_bev[
                (df_new_bev["Category"] == category)
                & (df_new_bev["Sub_Category"] == sub_category)
            ].copy()

            if len(df_filtered) == 0:
                print(f"      - No data for {category} - {sub_category}, skipping")
                continue

            # Group and count
            grouped = df_filtered.groupby(
                ["Year", "Month", "Region"], as_index=False
            ).agg(_03_P1_NewEV=("OBJECTID", "count"))

            # Add metadata
            grouped["Metric_Group"] = "Transport"
            grouped["Category"] = category
            grouped["Sub_Category"] = sub_category
            grouped["Fuel_Type"] = "BEV"

            all_results.append(grouped)
            print(
                f"      - {category} {sub_category}: {len(grouped):,} rows, "
                f"{grouped['_03_P1_NewEV'].sum():,.0f} new EVs purchased"
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
                "_03_P1_NewEV",
            ]
        ]

        # Step 3: Save analytics
        print("\n[3/3] Saving analytics...")
        self.write_csv(analytics_df, output_path)

        print(f"\n✓ Analytics complete: {len(analytics_df):,} rows saved")
        print(f"  Total new EVs purchased: {analytics_df['_03_P1_NewEV'].sum():,.0f}")
        print(
            f"  Years covered: {analytics_df['Year'].min()} - {analytics_df['Year'].max()}"
        )


def main():
    """Main function to run the analytics pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = settings.processed_dir / "waka_kotahi_mvr" / "mvr_processed.parquet"
    output_path = settings.metrics_dir / "waka_kotahi_mvr" / "03_P1_NewEV_analytics.csv"

    # Create analytics processor
    processor = WakaKotahiNewEVCountAnalytics()

    # Run the analytics process
    try:
        processor.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Analytics failed: {e}")
        raise


if __name__ == "__main__":
    main()
