"""Analytics: EMI Electricity Generation renewable share by region.

This script creates analytics-ready aggregated data showing
monthly renewable generation share by region.
"""

from pathlib import Path

from etl.core.config import get_settings
from etl.core.pipeline import AnalyticsLayer


class EMIGenerationAnalytics(AnalyticsLayer):
    """Analytics processor for renewable generation share."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Create renewable generation share analytics by region and time.

        Args:
            input_path: Path to processed EMI generation CSV
            output_path: Path to save analytics CSV
        """
        print(f"\n{'='*80}")
        print("EMI ELECTRICITY GENERATION: Analytics")
        print(f"{'='*80}")

        # Step 1: Load processed data
        print("\n[1/3] Loading processed data...")
        df = self.read_csv(input_path)
        print(f"      Loaded {len(df)} rows from {input_path.name}")

        # Step 2: Calculate analytics
        print("\n[2/3] Calculating renewable generation share...")

        # Aggregate by Year, Month, Region, and Type (renewable flag)
        grouped = df.groupby(["Year", "Month", "Region", "Type"], as_index=False).agg(
            kWh=("kWh", "sum")
        )
        print(
            f"      - Aggregated to {len(grouped)} rows by year, month, region, and fuel type"
        )

        # Calculate renewable share (Type = 1)
        grouped["Total_All_Fuels"] = grouped.groupby(["Year", "Month", "Region"])[
            "kWh"
        ].transform("sum")
        grouped["_12_P1_EnergyRenew"] = grouped["kWh"] / grouped["Total_All_Fuels"]

        # Filter to renewable type only
        analytics_df = grouped[grouped["Type"] == 1].copy()
        print(f"      - Filtered to renewable only: {len(analytics_df)} rows")

        # Add metadata fields
        analytics_df["Metric Group"] = "Energy"
        analytics_df["Category"] = "Grid"
        analytics_df["Sub-Category"] = "Renewable Share"

        # Final selection
        analytics_df = analytics_df[
            [
                "Year",
                "Month",
                "Region",
                "Metric Group",
                "Category",
                "Sub-Category",
                "_12_P1_EnergyRenew",
            ]
        ]

        print(
            f"      - Renewable share ranges from {analytics_df['_12_P1_EnergyRenew'].min():.2%} "
            f"to {analytics_df['_12_P1_EnergyRenew'].max():.2%}"
        )
        print(
            f"      - Average renewable share: {analytics_df['_12_P1_EnergyRenew'].mean():.2%}"
        )

        # Step 3: Save analytics
        print("\n[3/3] Saving analytics...")
        self.write_csv(analytics_df, output_path)

        print(f"\n✓ Analytics complete: {len(analytics_df)} rows saved")
        print(
            f"  Years covered: {analytics_df['Year'].min()} - {analytics_df['Year'].max()}"
        )
        print(f"  Regions: {', '.join(sorted(analytics_df['Region'].unique()))}")


def main():
    """Main function to run the analytics pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = (
        settings.processed_dir / "emi_generation" / "emi_generation_cleaned.csv"
    )
    output_path = (
        settings.analytics_dir / "emi_generation" / "emi_generation_analytics.csv"
    )

    # Create analytics processor
    processor = EMIGenerationAnalytics()

    # Run the analytics process
    try:
        processor.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Analytics failed: {e}")
        raise


if __name__ == "__main__":
    main()
