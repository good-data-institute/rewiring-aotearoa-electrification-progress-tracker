"""Analytics: GIC Gas Connections aggregated by region and time.

This script creates analytics-ready aggregated data showing
monthly new gas connections by region.
"""

from pathlib import Path

from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer


class GICGasConnectionsAnalytics(MetricsLayer):
    """Analytics processor for gas connections aggregation."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Create gas connections analytics aggregated by region and time.

        Args:
            input_path: Path to processed GIC gas connections CSV
            output_path: Path to save analytics CSV
        """
        print(f"\n{'=' * 80}")
        print("GIC GAS CONNECTIONS: Analytics")
        print(f"{'=' * 80}")

        # Step 1: Load processed data
        print("\n[1/3] Loading processed data...")
        df = self.read_csv(input_path)
        print(f"      Loaded {len(df)} rows from {input_path.name}")

        # Step 2: Calculate analytics
        print("\n[2/3] Aggregating gas connections by region and time...")

        # Group and sum new connections
        analytics_df = df.groupby(["Year", "Month", "Region"], as_index=False).agg(
            _10_P1_Gas=("NEW", "sum")
        )
        print(
            f"      - Aggregated to {len(analytics_df)} rows "
            f"({df['Year'].nunique()} years × {df['Month'].nunique()} months × {df['Region'].nunique()} regions)"
        )

        # Add metadata columns
        analytics_df = analytics_df.copy().assign(
            **{"Metric Group": "Energy", "Category": "Gas", "Sub-Category": "Total"}
        )

        print(f"      - Total new connections: {analytics_df['_10_P1_Gas'].sum():,.0f}")
        print(f"      - Average per month: {analytics_df['_10_P1_Gas'].mean():.1f}")

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
    input_path = settings.processed_dir / "gic" / "gic_gas_connections_cleaned.csv"
    output_path = settings.metrics_dir / "gic" / "gic_gas_connections_analytics.csv"

    # Create analytics processor
    processor = GICGasConnectionsAnalytics()

    # Run the analytics process
    try:
        processor.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Analytics failed: {e}")
        raise


if __name__ == "__main__":
    main()
