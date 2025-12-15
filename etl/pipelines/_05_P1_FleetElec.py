"""Analytics: Waka Kotahi MVR - Fleet Electrification Percentage.

This script creates analytics-ready aggregated data showing
the percentage of vehicle fleet that is electrified (BEV)
by region, category, and sub-category.

Metric ID: _05_P1_FleetElec
"""

from pathlib import Path

import pandas as pd

from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer


class WakaKotahiFleetElectrificationAnalytics(MetricsLayer):
    """Analytics processor for fleet electrification percentage."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Create fleet electrification percentage analytics by region, category, and time.

        Args:
            input_path: Path to processed MVR Parquet file
            output_path: Path to save analytics CSV
        """
        print(f"\n{'=' * 80}")
        print("WAKA KOTAHI MVR: Fleet Electrification % Analytics (_05_P1_FleetElec)")
        print(f"{'=' * 80}")

        # Step 1: Load processed data
        print("\n[1/3] Loading processed data...")
        df = pd.read_parquet(input_path)
        print(f"      Loaded {len(df):,} rows from {input_path.name}")

        # Step 2: Calculate analytics
        print("\n[2/3] Calculating fleet electrification percentages...")

        # Define the category/sub-category combinations we want
        category_combinations = [
            ("Private", "Light Passenger Vehicle"),
            ("Commercial", "Light Passenger Vehicle"),
            ("Private", "Light Commercial Vehicle"),
            ("Commercial", "Light Commercial Vehicle"),
        ]

        all_results = []

        for category, sub_category in category_combinations:
            # Filter data for this category/sub-category
            df_filtered = df[
                (df["Category"] == category) & (df["Sub_Category"] == sub_category)
            ].copy()

            if len(df_filtered) == 0:
                print(f"      - No data for {category} - {sub_category}, skipping")
                continue

            # Calculate total fleet count
            total_fleet = (
                df_filtered.groupby(["Year", "Month", "Region"])["OBJECTID"]
                .count()
                .rename("total_fleet")
            )

            # Calculate EV (BEV) fleet count
            ev_fleet = (
                df_filtered[df_filtered["Fuel_Type"] == "BEV"]
                .groupby(["Year", "Month", "Region"])["OBJECTID"]
                .count()
                .rename("ev_fleet")
            )

            # Merge and calculate percentage
            grouped = pd.merge(
                total_fleet, ev_fleet, left_index=True, right_index=True, how="left"
            ).fillna(0)

            # Calculate percentage (0-100 scale)
            grouped["_05_P1_FleetElec"] = (
                grouped["ev_fleet"] / grouped["total_fleet"] * 100
            )
            grouped = grouped.reset_index()

            # Add metadata
            grouped["Metric_Group"] = "Transport"
            grouped["Category"] = category
            grouped["Sub_Category"] = sub_category
            grouped["Fuel_Type"] = None  # N/A for percentage metrics

            # Select final columns
            grouped = grouped[
                [
                    "Year",
                    "Month",
                    "Region",
                    "Metric_Group",
                    "Category",
                    "Sub_Category",
                    "Fuel_Type",
                    "_05_P1_FleetElec",
                ]
            ]

            all_results.append(grouped)
            avg_percent = grouped["_05_P1_FleetElec"].mean()
            max_percent = grouped["_05_P1_FleetElec"].max()
            print(
                f"      - {category} {sub_category}: {len(grouped):,} rows, "
                f"avg: {avg_percent:.2f}%, max: {max_percent:.2f}%"
            )

        # Combine all results
        analytics_df = pd.concat(all_results, ignore_index=True)

        # Step 3: Save analytics
        print("\n[3/3] Saving analytics...")
        self.write_csv(analytics_df, output_path)

        print(f"\n✓ Analytics complete: {len(analytics_df):,} rows saved")
        print(
            f"  Overall average electrification: {analytics_df['_05_P1_FleetElec'].mean():.2f}%"
        )
        print(
            f"  Years covered: {analytics_df['Year'].min()} - {analytics_df['Year'].max()}"
        )


def main():
    """Main function to run the analytics pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = settings.processed_dir / "waka_kotahi_mvr" / "mvr_processed.parquet"
    output_path = (
        settings.metrics_dir / "waka_kotahi_mvr" / "05_P1_FleetElec_analytics.csv"
    )

    # Create analytics processor
    processor = WakaKotahiFleetElectrificationAnalytics()

    # Run the analytics process
    try:
        processor.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Analytics failed: {e}")
        raise


if __name__ == "__main__":
    main()
