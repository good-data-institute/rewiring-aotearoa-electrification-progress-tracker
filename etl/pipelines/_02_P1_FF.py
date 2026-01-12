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
from etl.core.mappings import EV_REGION_MAP


class WakaKotahiFossilFuelCountAnalytics(MetricsLayer):
    """Analytics processor for fossil fuel vehicle count aggregation."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Create fossil fuel vehicle count analytics by region, category, and time.

        Args:
            input_path: Path to processed MVR Parquet file
            output_path: Path to save analytics CSV
        """
        print(f"\n{'=' * 80}")
        print("WAKA KOTAHI MVR: Fossil Fuel Vehicle Count Analytics (_02_P1_FF)")
        print(f"{'=' * 80}")

        # Step 1: Load processed data
        print("\n[1/3] Loading processed data...")
        df = pd.read_parquet(input_path)
        print(f"      Loaded {len(df):,} rows from {input_path.name}")

        # Step 2: Calculate analytics
        print("\n[2/3] Aggregating fossil fuel vehicle counts...")

        # Assign Districts to Regions
        df["Region"] = df["Region"].fillna("UNKNOWN")
        df_reg = df.rename(columns={"Region": "District"})
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
                df_filtered = df_reg[
                    (df_reg["Fuel_Type"] == fuel_type)
                    & (df_reg["Category"] == category)
                    & (df_reg["Sub_Category"] == sub_category)
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
        comb_df = pd.concat(all_results, ignore_index=True)

        # Add a total group
        total_grouped = comb_df.groupby(["Year", "Month", "Region"], as_index=False)[
            "_02_P1_FF"
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
        ]

        ntots = analytics_df[
            (analytics_df["Category"] != "Total")
            & (analytics_df["Sub_Category"] != "Total")
            & (analytics_df["Fuel_Type"] != "Total")
        ]

        assert (
            tots["_02_P1_FF"].sum() == ntots["_02_P1_FF"].sum()
        ), f"Totals mismatch: Total={tots}, Non-Totals={ntots}"

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
        print(f"  Total fossil fuel vehicles: {ntots["_02_P1_FF"].sum():,.0f}")
        print(f"  Years covered: {ntots['Year'].min()} - {ntots['Year'].max()}")
        print(f"  Fuel types: {', '.join(sorted(ntots['Fuel_Type'].unique()))}")
        print(f"  Category: {', '.join(sorted(ntots['Category'].unique()))}")
        print(f"  Sub_Category: {', '.join(sorted(ntots['Sub_Category'].unique()))}")


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
