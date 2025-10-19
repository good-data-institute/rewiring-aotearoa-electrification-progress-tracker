"""Analytics: EECA Electricity Consumption Percentage.

This script creates analytics-ready aggregated data showing
electricity's share of total energy consumption over time.
"""

from pathlib import Path

from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer


class EECAElectricityPercentageAnalytics(MetricsLayer):
    """Analytics processor for electricity consumption percentage."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Create electricity consumption percentage analytics.

        Calculates the percentage of total energy consumption that comes
        from electricity, aggregated by year.

        Args:
            input_path: Path to processed EECA energy consumption CSV
            output_path: Path to save analytics CSV
        """
        print(f"\n{'='*80}")
        print("EECA ELECTRICITY PERCENTAGE: Analytics")
        print(f"{'='*80}")

        # Step 1: Load processed data
        print("\n[1/3] Loading processed data...")
        df = self.read_csv(input_path)
        print(f"      Loaded {len(df)} rows from {input_path.name}")

        # Step 2: Calculate analytics
        print("\n[2/3] Calculating electricity consumption percentage...")

        # Total energy by year
        total_energy = (
            df.groupby("Year", as_index=False)["energyValue"]
            .sum()
            .rename(columns={"energyValue": "Total_Energy"})
        )
        print(f"      - Calculated total energy for {len(total_energy)} years")

        # Electricity energy by year
        electricity_energy = (
            df.query("Category == 'Electricity'")
            .groupby("Year", as_index=False)["energyValue"]
            .sum()
            .rename(columns={"energyValue": "Electricity_Energy"})
        )
        print(
            f"      - Calculated electricity energy for {len(electricity_energy)} years"
        )

        # Merge and calculate the share
        analytics_df = total_energy.merge(
            electricity_energy, on="Year", how="left"
        ).assign(
            _13_P1_ElecCons=lambda x: 100 * x["Electricity_Energy"] / x["Total_Energy"]
        )[["Year", "_13_P1_ElecCons"]]

        # Add metadata
        analytics_df["Metric Group"] = "Energy"
        analytics_df["Category"] = "Consumption"
        analytics_df["Sub-Category"] = "Electricity Share"

        print(
            f"      - Electricity share ranges from {analytics_df['_13_P1_ElecCons'].min():.2f}% "
            f"to {analytics_df['_13_P1_ElecCons'].max():.2f}%"
        )

        # Step 3: Save analytics
        print("\n[3/3] Saving analytics...")
        self.write_csv(analytics_df, output_path)

        print(f"\n✓ Analytics complete: {len(analytics_df)} rows saved")
        print(
            f"  Years covered: {analytics_df['Year'].min()} - {analytics_df['Year'].max()}"
        )


def main():
    """Main function to run the analytics pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = settings.processed_dir / "eeca" / "eeca_energy_consumption_cleaned.csv"
    output_path = settings.analytics_dir / "eeca" / "eeca_electricity_percentage.csv"

    # Create analytics processor
    processor = EECAElectricityPercentageAnalytics()

    # Run the analytics process
    try:
        processor.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Analytics failed: {e}")
        raise


if __name__ == "__main__":
    main()
