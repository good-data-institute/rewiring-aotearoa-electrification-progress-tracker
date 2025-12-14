"""
Analytics: EECA Charging Stations - Total Points Metric

This script creates analytics-ready aggregated data showing:
- Total charging points by Year, Month, and Region
in a single CSV file.

Metric Group: Transport
Category: Public
Sub-Category: Charging Station
Metric ID: _bonus_ChargingStations
"""

from pathlib import Path
import pandas as pd
from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer


class EECAChargingStationsMetrics(MetricsLayer):
    """Analytics processor for EECA Charging Stations."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Create charging station metrics aggregated by Year, Month, and Region (Locality and District could also be used).

        Args:
            input_path: Path to raw CSV file
            output_path: Path to save combined metrics CSV
        """
        print(f"\n{'='*80}")
        print(
            "EECA CHARGING STATIONS: Metrics - Total Points (_bonus_ChargingStations)"
        )
        print(f"{'='*80}")

        # Step 1: Load raw data
        print("\n[1/3] Loading data...")
        df = pd.read_csv(input_path)
        print(f"      Loaded {len(df):,} rows from {input_path.name}")

        # Step 2: Clean / convert columns
        print("\n[2/3] Cleaning and converting data...")
        df["Points"] = pd.to_numeric(df["Points"], errors="coerce").fillna(0)
        df["DateFirstOperational"] = pd.to_datetime(
            df["DateFirstOperational"], errors="coerce"
        )
        df["Year"] = df["DateFirstOperational"].dt.year
        df["Month"] = df["DateFirstOperational"].dt.month

        # Step 3: Aggregate by Year, Month, and Region (Locality and District could also be used)
        print("\n[3/3] Aggregating total points by Year, Month, and Region...")
        metrics_df = (
            df.groupby(["Year", "Month", "Region"], as_index=False)["Points"]
            .sum()
            .rename(columns={"Points": "_bonus_ChargingStations"})
        )

        # Add static metadata columns
        metrics_df["Metric_Group"] = "Transport"
        metrics_df["Category"] = "Public"
        metrics_df["Sub_Category"] = "Charging Station"

        # Reorder columns to match desired output
        metrics_df = metrics_df[
            [
                "Year",
                "Month",
                "Region",
                "Metric_Group",
                "Category",
                "Sub_Category",
                "_bonus_ChargingStations",
            ]
        ]

        # Step 4: Save CSV
        output_path.parent.mkdir(parents=True, exist_ok=True)
        metrics_df.to_csv(output_path, index=False)
        print(f"      ✓ Saved metrics CSV: {output_path}")

        print(f"\n{'='*80}")
        print("✓ EECA Charging Stations metrics complete")
        print(
            f"  Years covered: {metrics_df['Year'].min()} - {metrics_df['Year'].max()}"
        )
        print(f"  Regions covered: {metrics_df['Region'].nunique()}")
        print(f"{'='*80}\n")


def main():
    """Main function to run the EECA Charging Stations metrics pipeline."""
    settings = get_settings()

    # Input raw CSV from extractor
    input_path = settings.raw_dir / "eeca" / "eeca_charging_stations_raw.csv"
    # Output CSV for combined metrics
    output_path = settings.metrics_dir / "eeca" / "bonus_ChargingStations_analytics.csv"

    processor = EECAChargingStationsMetrics()

    try:
        processor.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Metrics computation failed: {e}")
        raise


if __name__ == "__main__":
    main()
