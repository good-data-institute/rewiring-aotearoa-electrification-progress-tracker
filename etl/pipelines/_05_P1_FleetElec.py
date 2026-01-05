"""
Analytics: Waka Kotahi MVR - Fleet Electrification Percentage.

This script creates analytics-ready aggregated data showing
the percentage of the vehicle fleet that is electrified (BEV)
by year, month, and region.

Fleet model:
- One row per vehicle (OBJECTID)
- Vehicle enters fleet at its earliest observed registration event
- Vehicles remain in fleet indefinitely (no scrappage model)

Metric ID: _05_P1_FleetElec
"""

from pathlib import Path

import pandas as pd

from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer
from etl.core.mappings import EV_REGION_MAP


class WakaKotahiFleetElectrificationAnalytics(MetricsLayer):
    """Analytics processor for fleet electrification percentage."""

    def process(self, input_path: Path, output_path: Path) -> None:
        print(f"\n{'=' * 80}")
        print("WAKA KOTAHI MVR: Fleet Electrification % Analytics (_05_P1_FleetElec)")
        print(f"{'=' * 80}")

        # ------------------------------------------------------------------
        # Step 1: Load processed data
        # ------------------------------------------------------------------
        print("\n[1/4] Loading processed data...")
        df = pd.read_parquet(input_path)
        print(f"      Loaded {len(df):,} rows")

        # ------------------------------------------------------------------
        # Step 2: Reduce to one row per vehicle (earliest observed event)
        # ------------------------------------------------------------------
        print("\n[2/4] Identifying first observed registration per vehicle...")

        df = df.sort_values(["OBJECTID", "Year", "Month"])

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

        vehicles = df_reg.groupby("OBJECTID", as_index=False).first()

        print(f"      Identified {len(vehicles):,} unique vehicles")

        # ------------------------------------------------------------------
        # Step 3: Build cumulative fleet counts by region
        # ------------------------------------------------------------------
        print("\n[3/4] Building cumulative fleet...")

        # Vehicles entering fleet per month
        fleet_additions = (
            vehicles.groupby(["Year", "Month", "Region"])["OBJECTID"]
            .count()
            .rename("new_vehicles")
        )

        # BEV vehicles entering fleet per month
        ev_additions = (
            vehicles[vehicles["Fuel_Type"] == "BEV"]
            .groupby(["Year", "Month", "Region"])["OBJECTID"]
            .count()
            .rename("new_ev_vehicles")
        )

        # Merge monthly additions
        fleet = (
            pd.merge(
                fleet_additions,
                ev_additions,
                left_index=True,
                right_index=True,
                how="left",
            )
            .fillna(0)
            .sort_index()
        )

        # Cumulative totals per region
        fleet["total_fleet"] = fleet.groupby(level="Region")["new_vehicles"].cumsum()

        fleet["ev_fleet"] = fleet.groupby(level="Region")["new_ev_vehicles"].cumsum()

        # Fleet electrification %
        fleet["_05_P1_FleetElec"] = fleet["ev_fleet"] / fleet["total_fleet"] * 100

        fleet = fleet.reset_index()

        # ------------------------------------------------------------------
        # Step 4: Finalise output
        # ------------------------------------------------------------------
        fleet["Metric_Group"] = "Transport"
        fleet["Category"] = "Total"
        fleet["Sub_Category"] = "Total"
        fleet["Fuel_Type"] = "BEV"

        analytics_df = fleet[
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

        # ------------------------------------------------------------------
        # Sanity checks
        # ------------------------------------------------------------------
        max_pct = analytics_df["_05_P1_FleetElec"].max()
        min_pct = analytics_df["_05_P1_FleetElec"].min()

        print(f"      Fleet electrification range: " f"{min_pct:.3f}% – {max_pct:.3f}%")

        assert 0 <= min_pct
        assert max_pct <= 5, "Fleet electrification unexpectedly high"

        # ------------------------------------------------------------------
        # Step 5: Save analytics
        # ------------------------------------------------------------------
        print("\n[4/4] Saving analytics...")
        self.write_csv(analytics_df, output_path)

        print(f"\n✓ Analytics complete: {len(analytics_df):,} rows saved")
        print(
            f"  Years covered: {analytics_df['Year'].min()} – "
            f"{analytics_df['Year'].max()}"
        )


def main():
    settings = get_settings()

    input_path = settings.processed_dir / "waka_kotahi_mvr" / "mvr_processed.parquet"

    output_path = (
        settings.metrics_dir / "waka_kotahi_mvr" / "05_P1_FleetElec_analytics.csv"
    )

    processor = WakaKotahiFleetElectrificationAnalytics()

    try:
        processor.process(
            input_path=input_path,
            output_path=output_path,
        )
    except Exception as e:
        print(f"\n✗ Analytics failed: {e}")
        raise


if __name__ == "__main__":
    main()
