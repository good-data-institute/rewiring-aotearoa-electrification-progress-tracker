"""Analytics: EMI Electricity Generation renewable share by region.

This script creates analytics-ready aggregated data showing
monthly renewable generation share by region.
"""

from pathlib import Path
import pandas as pd

from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer


class EMIGenerationAnalytics(MetricsLayer):
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
        grouped["EnergyRenew"] = grouped["kWh"] / grouped["Total_All_Fuels"]

        # Filter to renewable type only
        grouped = grouped[grouped["Type"] == 1].copy()
        print(f"      - Filtered to renewable only: {len(grouped)} rows")

        # Create a sortable date column
        grouped["date"] = pd.to_datetime(
            dict(year=grouped["Year"], month=grouped["Month"], day=1)
        )

        # Sort to ensure correct order for rolling calculations
        interim_df = grouped.sort_values(["date"]).reset_index(drop=True)

        # Calculate 12-month rolling mean
        # The 'rolling(12)' means each value is the mean of the current and previous 11 months
        interim_df["_12_P1_EnergyRenew"] = (
            interim_df["EnergyRenew"].rolling(window=12, min_periods=12).mean()
        )
        interim_df2 = interim_df.dropna(subset=["_12_P1_EnergyRenew"])
        print(
            f"      - Calculated rolling mean, dropped {len(interim_df) - len(interim_df2)} rows"
        )

        # Add metadata fields
        interim_df2 = interim_df2.copy().assign(
            **{"Metric Group": "Energy", "Category": "Grid", "Sub-Category": ""}
        )

        # Final selection
        out_df = interim_df2[
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
            f"      - Renewable share ranges from {out_df['_12_P1_EnergyRenew'].min():.2%} "
            f"to {out_df['_12_P1_EnergyRenew'].max():.2%}"
        )
        print(
            f"      - Average renewable share: {out_df['_12_P1_EnergyRenew'].mean():.2%}"
        )

        # Step 3: Save analytics
        print("\n[3/3] Saving analytics...")
        self.write_csv(out_df, output_path)

        print(f"\n✓ Analytics complete: {len(out_df)} rows saved")
        print(f"  Years covered: {out_df['Year'].min()} - {out_df['Year'].max()}")
        print(f"  Regions: {', '.join(sorted(out_df['Region'].unique()))}")


def main():
    """Main function to run the analytics pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = (
        settings.processed_dir / "emi_generation" / "emi_generation_cleaned.csv"
    )
    output_path = (
        settings.metrics_dir / "emi_generation" / "emi_generation_analytics.csv"
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
