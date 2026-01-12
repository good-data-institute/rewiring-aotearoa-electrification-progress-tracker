"""Analytics: Waka Kotahi MVR - Number of Used EVs purchased.

This script creates analytics-ready aggregated data showing
monthly used (imported) electric vehicle (BEV) purchase counts
by region, category, and sub-category.

Metric ID: _04_P1_UsedEV
"""

from pathlib import Path

import pandas as pd

from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer
from etl.core.mappings import EV_REGION_MAP


class WakaKotahiUsedEVCountAnalytics(MetricsLayer):
    """Analytics processor for used EV purchase count aggregation."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Create used EV purchase count analytics by region, category, and time.

        Args:
            input_path: Path to processed MVR Parquet file
            output_path: Path to save analytics CSV
        """
        print(f"\n{'=' * 80}")
        print("WAKA KOTAHI MVR: Used EV Purchase Count Analytics (_04_P1_UsedEV)")
        print(f"{'=' * 80}")

        # Step 1: Load processed data
        print("\n[1/3] Loading processed data...")
        df = pd.read_parquet(input_path)
        print(f"      Loaded {len(df):,} rows from {input_path.name}")

        # Step 2: Calculate analytics
        print("\n[2/3] Aggregating used EV purchase counts...")

        # Filter for USED BEVs only
        df_used_bev = df[
            (df["Fuel_Type"] == "BEV") & (df["Condition"] == "USED")
        ].copy()
        print(f"      - Filtered to {len(df_used_bev):,} used BEV records")

        # Assign Districts to Regions
        df_used_bev["Region"] = df_used_bev["Region"].fillna("UNKNOWN")
        df_reg = df_used_bev.rename(columns={"Region": "District"})
        df_reg["Region"] = df_reg["District"].map(EV_REGION_MAP)

        # identify unmapped districts
        missing = df_reg[df_reg["Region"].isna()]["District"].unique()

        if len(missing) > 0:
            print("      ! Unmapped districts found:")
            for d in missing:
                print(f"        • {d}")
        else:
            print("      - All districts mapped cleanly.")
        print(
            f"      - Districts (n = {df_reg['District'].nunique()}) "
            f"mapped to Regions (n = {df_reg['Region'].nunique()})"
        )

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
            df_filtered = df_used_bev[
                (df_used_bev["Category"] == category)
                & (df_used_bev["Sub_Category"] == sub_category)
            ].copy()

            if len(df_filtered) == 0:
                print(f"      - No data for {category} - {sub_category}, skipping")
                continue

            # Group and count
            grouped = df_filtered.groupby(
                ["Year", "Month", "Region"], as_index=False
            ).agg(_04_P1_UsedEV=("OBJECTID", "count"))

            # Add metadata
            grouped["Metric_Group"] = "Transport"
            grouped["Category"] = category
            grouped["Sub_Category"] = sub_category
            grouped["Fuel_Type"] = "BEV"

            all_results.append(grouped)
            print(
                f"      - {category} {sub_category}: {len(grouped):,} rows, "
                f"{grouped['_04_P1_UsedEV'].sum():,.0f} used EVs purchased"
            )

        # Combine all results
        analytics_df = pd.concat(all_results, ignore_index=True)
        comb_df = pd.concat(all_results, ignore_index=True)

        # Add a total group
        total_grouped = comb_df.groupby(["Year", "Month", "Region"], as_index=False)[
            "_04_P1_UsedEV"
        ].sum()
        total_grouped = total_grouped.assign(
            **{
                "Metric_Group": "Transport",
                "Category": "Total",
                "Sub_Category": "Total",
                "Fuel_Type": "Total",
            }
        )

        # Combine all results
        analytics_df = comb_df._append(total_grouped)
        print("      - Added 'Total' groups to Category, Sub_Category and Fuel_Type")

        # Check that totals operate as expected
        tots = analytics_df[
            (analytics_df["Category"] == "Total")
            & (analytics_df["Sub_Category"] == "Total")
            & (analytics_df["Fuel_Type"] == "Total")
        ]["_04_P1_UsedEV"].sum()

        ntots = analytics_df[
            (analytics_df["Category"] != "Total")
            & (analytics_df["Sub_Category"] != "Total")
            & (analytics_df["Fuel_Type"] != "Total")
        ]["_04_P1_UsedEV"].sum()

        assert tots == ntots, f"Totals mismatch: Total={tots}, Non-Totals={ntots}"

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
                "_04_P1_UsedEV",
            ]
        ]

        # Step 3: Save analytics
        print("\n[3/3] Saving analytics...")
        self.write_csv(analytics_df, output_path)

        print(f"\n✓ Analytics complete: {len(analytics_df):,} rows saved")
        print(f"  Total used EVs purchased: {analytics_df['_04_P1_UsedEV'].sum():,.0f}")
        print(
            f"  Years covered: {analytics_df['Year'].min()} - {analytics_df['Year'].max()}"
        )


def main():
    """Main function to run the analytics pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = settings.processed_dir / "waka_kotahi_mvr" / "mvr_processed.parquet"
    output_path = (
        settings.metrics_dir / "waka_kotahi_mvr" / "04_P1_UsedEV_analytics.csv"
    )

    # Create analytics processor
    processor = WakaKotahiUsedEVCountAnalytics()

    # Run the analytics process
    try:
        processor.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Analytics failed: {e}")
        raise


if __name__ == "__main__":
    main()
