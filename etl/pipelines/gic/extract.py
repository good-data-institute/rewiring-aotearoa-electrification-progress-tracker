"""Extract: GIC Gas Connections data pipeline.

This script handles raw data extraction:
1. Extracts raw Excel data from GIC Registry Statistics
2. Saves raw data exactly as received (no cleaning/transformation)
"""

from pathlib import Path

from etl.apis.gic import GICAPI
from etl.core.config import get_settings


class GICGasConnectionsExtractor:
    """Data extractor for GIC Gas Connections: Extract from API to raw storage."""

    def __init__(self):
        """Initialize extractor with API client."""
        self.api = GICAPI()

    def extract(self, output_path: Path) -> None:
        """Extract raw data from API.

        Args:
            output_path: Path to save raw Excel file
        """
        print(f"\n{'='*80}")
        print("GIC GAS CONNECTIONS: Extract Raw Data")
        print(f"{'='*80}")

        print("\n[1/1] Extracting data from GIC Registry Statistics...")
        print(f"      URL: {self.api.params.url}")
        print(f"      Output: {output_path}")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Fetch raw Excel data
        excel_data = self.api.fetch_data()

        # Save raw bytes to file
        with open(output_path, "wb") as f:
            f.write(excel_data)

        print("      ✓ Raw Excel file saved")

        print(f"\n{'='*80}")
        print(f"✓ Extraction complete: {output_path}")
        print(f"{'='*80}\n")


def main():
    """Main function to run the extraction pipeline."""
    settings = get_settings()

    # Define output path in raw directory
    output_path = settings.raw_dir / "gic" / "gic_gas_connections_raw.xlsx"

    # Create extractor
    extractor = GICGasConnectionsExtractor()

    # Run the extraction process
    try:
        extractor.extract(output_path=output_path)
    except Exception as e:
        print(f"\n✗ Extraction failed: {e}")
        raise


if __name__ == "__main__":
    main()
