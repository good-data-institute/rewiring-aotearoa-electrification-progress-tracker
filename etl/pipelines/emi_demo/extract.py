"""Extract: EMI Retail data pipeline.

This script handles raw data extraction:
1. Extracts raw data from EMI Retail API
2. Saves raw data exactly as received (no cleaning/transformation)
"""

from pathlib import Path

from etl.apis.emi_retail import EMIRetailAPI
from etl.core.config import get_settings


class EMIRetailExtractor:
    """Data extractor for EMI Retail: Extract from API to raw storage."""

    def __init__(
        self,
        report_id: str = "GUEHMT",
        capacity: str = "All_Drilldown",
        date_from: str = "20250801",
        date_to: str = "20250831",
        region_type: str = "NZ",
        fuel_type: str = "All_Drilldown",
    ):
        """Initialize extractor with API parameters.

        Args:
            report_id: EMI report ID
            capacity: Capacity filter
            date_from: Start date (YYYYMMDD)
            date_to: End date (YYYYMMDD)
            region_type: Region type filter
            fuel_type: Fuel type filter
        """
        self.api = EMIRetailAPI(
            report_id=report_id,
            Capacity=capacity,
            DateFrom=date_from,
            DateTo=date_to,
            RegionType=region_type,
            FuelType=fuel_type,
        )

    def extract(self, output_path: Path) -> None:
        """Extract raw data from API.

        Args:
            output_path: Path to save raw CSV file
        """
        print(f"\n{'='*80}")
        print("EMI RETAIL: Extract Raw Data")
        print(f"{'='*80}")

        print("\n[1/1] Extracting data from EMI Retail API...")
        print(f"      Parameters: {self.api.params.model_dump()}")
        print(f"      Output: {output_path}")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Fetch raw data and save exactly as received
        self.api.fetch_data(output_path=output_path)
        print("      ✓ Raw data saved")

        print(f"\n{'='*80}")
        print(f"✓ Extraction complete: {output_path}")
        print(f"{'='*80}\n")


def main():
    """Main function to run the extraction pipeline."""
    settings = get_settings()

    # Define output path in raw directory
    output_path = settings.raw_dir / "emi_retail" / "emi_retail_20250801_20250831.csv"

    # Create extractor with default parameters
    extractor = EMIRetailExtractor(
        report_id="GUEHMT",
        capacity="All_Drilldown",
        date_from="20250801",
        date_to="20250831",
        region_type="NZ",
        fuel_type="All_Drilldown",
    )

    # Run the extraction process
    try:
        extractor.extract(output_path=output_path)
    except Exception as e:
        print(f"\n✗ Extraction failed: {e}")
        raise


if __name__ == "__main__":
    main()
