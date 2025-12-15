"""Extract: EECA Charging Stations data pipeline.

This script handles raw data extraction:
1. Downloads raw CSV data from EECA Public EV Charger Dashboard
2. Saves raw data exactly as received (no cleaning/transformation)
"""

from pathlib import Path

from etl.apis.eeca import EECAAPI
from etl.core.config import get_settings


class EECAChargingStationsExtractor:
    """Data extractor for EECA Charging Stations: Extract from API to raw storage."""

    def __init__(self, url: str):
        """Initialize extractor with API client and chargin stations URL."""
        self.api = EECAAPI(url=url)

    def extract(self, output_path: Path) -> None:
        """Extract raw data from API.

        Args:
            output_path: Path to save raw Excel file
        """
        print(f"\n{'=' * 80}")
        print("EECA CHARGING STATIONS: Extract Raw Data")
        print(f"{'=' * 80}")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print("\n[1/1] Extracting charging stations data from EECA database...")
        print(f"      URL: {self.api.params.url}")

        # Fetch raw Excel data
        csv_data = self.api.fetch_data()

        # Save raw bytes to file
        with open(output_path, "wb") as f:
            f.write(csv_data)

        print("      ✓ Raw Excel file saved")

        print(f"\n{'=' * 80}")
        print(f"✓ Extraction complete: {output_path}")
        print(f"{'=' * 80}\n")


def main():
    """Main function to run the extraction pipeline."""
    settings = get_settings()

    # Define output path in raw directory
    output_path = settings.raw_dir / "eeca" / "eeca_charging_stations_raw.csv"

    # Create extractor
    extractor = EECAChargingStationsExtractor(
        url="http://eeca.govt.nz/assets/EECA-Resources/Public-EV-Charger-Dashboard/Public-EV-chargers.csv"
    )

    # Run the extraction process
    try:
        extractor.extract(output_path=output_path)
    except Exception as e:
        print(f"\n✗ Extraction failed: {e}")
        raise


if __name__ == "__main__":
    main()
