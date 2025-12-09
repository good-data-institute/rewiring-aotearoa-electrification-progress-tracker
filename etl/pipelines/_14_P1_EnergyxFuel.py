"""Analytics: EECA Energy Consumption by Fuel Type.

This script creates analytics-ready aggregated data showing
energy consumption by year, fuel type (category), and sector (sub-category).
Converts energy values from terajoules to MWh.
"""

from pathlib import Path

from etl.core.config import get_settings
from etl.core.pipeline import MetricsLayer
import math


class EECAEnergyByFuelAnalytics(MetricsLayer):
    """Analytics processor for energy consumption by fuel type."""

    def process(self, input_path: Path, output_path: Path) -> None:
        """Create energy consumption by fuel type analytics.

        Aggregates energy consumption by Year, Category (fuel type),
        and Sub-Category (sector), then converts from terajoules to MWh.

        Args:
            input_path: Path to processed EECA energy consumption CSV
            output_path: Path to save analytics CSV
        """
        print(f"\n{'=' * 80}")
        print("EECA ENERGY BY FUEL TYPE: Analytics")
        print(f"{'=' * 80}")

        # Step 1: Load processed data -----------------------------------------
        print("\n[1/7] Loading processed data...")
        df = self.read_csv(input_path)
        print(f"      Loaded {len(df)} rows from {input_path.name}")

        # Step 2: Aggregate by Category and Sub-Category ----------------------
        print("\n[2/7] Aggregating energy consumption by fuel type and sector")

        # Group and summarise
        group_cat_sub = df.groupby(
            ["Year", "Category", "Sub-Category"], as_index=False
        )["energyValue"].sum()
        print(
            f"      - Aggregated to {len(group_cat_sub)} rows "
            f"({df['Year'].nunique()} years × {df['Category'].nunique()} fuel types × {df['Sub-Category'].nunique()} sectors)"
        )

        # Step 3: Aggregate by Sub-Category -----------------------------------
        print("\n[3/7] Aggregating energy consumption by sector")

        # Group and summarise
        group_sub = df.groupby(["Year", "Sub-Category"], as_index=False)[
            "energyValue"
        ].sum()
        group_sub = group_sub.assign(**{"Category": "Total"})
        print(
            f"      - Aggregated to {len(group_sub)} rows "
            f"({df['Year'].nunique()} years × {df['Sub-Category'].nunique()} sectors)"
        )

        # Step 4: Aggregate by Category ---------------------------------------
        print("\n[4/7] Aggregating energy consumption by fuel type")

        # Group and summarise
        group_cat = df.groupby(["Year", "Category"], as_index=False)[
            "energyValue"
        ].sum()
        group_cat = group_cat.assign(**{"Sub-Category": "Total"})
        print(
            f"      - Aggregated to {len(group_cat)} rows "
            f"({df['Year'].nunique()} years × {df['Category'].nunique()} fuel types)"
        )

        # Step 5: Aggregate ---------------------------------------------------
        print("\n[5/7] Aggregating energy consumption across fuel types and sectors")

        # Group and summarise
        group = df.groupby("Year", as_index=False)["energyValue"].sum()
        group = group.assign(**{"Sub-Category": "Total", "Category": "Total"})
        print(f"      - Aggregated to {len(group)} rows ({df['Year'].nunique()} years)")

        # Step 6: Join datasets -----------------------------------------------
        print("\n[6/7] Add a Total Category to Sector")
        out_df = group_cat_sub._append(group_cat)._append(group_sub)._append(group)

        # Add metadata
        out_df = out_df.assign(
            **{"Metric Group": "Energy", "Month": "Total", "Region": "Total"}
        )

        # Convert to MWh instead of Terajoules
        out_df["_14_P1_EnergyxFuel"] = out_df["energyValue"] * (1 / 0.036)
        out_df = out_df.drop(columns=["energyValue"])
        print("      - Converted from terajoules to MWh using factor (1 / 0.036)")
        print(f"      - Total energy: {out_df['_14_P1_EnergyxFuel'].sum():,.0f} MWh")

        # Test aggregates
        lhs = out_df[
            (out_df["Year"] == 2017)
            & (out_df["Category"] == "Total")
            & (out_df["Sub-Category"] == "Total")
        ]["_14_P1_EnergyxFuel"].iloc[0]

        rhs = out_df[
            (out_df["Year"] == 2017)
            & (out_df["Category"] != "Total")
            & (out_df["Sub-Category"] != "Total")
        ]["_14_P1_EnergyxFuel"].sum()

        assert math.isclose(
            lhs, rhs, rel_tol=1e-12, abs_tol=1e-12
        ), "Totals do not match"
        print("      - Aggregation Check Passed (for 2017)")

        # Step 7: Save analytics ----------------------------------------------
        print("\n[7/7] Saving analytics...")
        self.write_csv(out_df, output_path)

        print(f"\n✓ Analytics complete: {len(out_df)} rows saved")
        print(f"  Years covered: {out_df['Year'].min()} - {out_df['Year'].max()}")
        print(f"  Fuel types: {', '.join(sorted(out_df['Category'].unique()))}")
        print(f"  Sectors: {out_df['Sub-Category'].unique()}")


def main():
    """Main function to run the analytics pipeline."""
    settings = get_settings()

    # Define input and output paths
    input_path = settings.processed_dir / "eeca" / "eeca_energy_consumption_cleaned.csv"
    output_path = settings.metrics_dir / "eeca" / "eeca_energy_by_fuel.csv"

    # Create analytics processor
    processor = EECAEnergyByFuelAnalytics()

    # Run the analytics process
    try:
        processor.process(input_path=input_path, output_path=output_path)
    except Exception as e:
        print(f"\n✗ Analytics failed: {e}")
        raise


if __name__ == "__main__":
    main()
