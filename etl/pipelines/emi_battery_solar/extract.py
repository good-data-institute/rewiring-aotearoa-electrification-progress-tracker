"""Extract: EMI Battery and Solar data pipeline.

This script handles raw data extraction:
1. Extracts raw CSV files from EMI website dashboard (multiple files)
2. Saves raw data exactly as received (no cleaning/transformation)
"""

from pathlib import Path
import json
from io import BytesIO

import pandas as pd
from etl.core.config import get_settings
from etl.apis.emi_retail import EMIRetailAPI


class EMIBatterySolarExtractor:
    """Data extractor for EMI Battery and Solar: Extract from website dashboard to raw storage."""

    def __init__(self):
        # Define market segments to extract
        self.market_segments = [
            ("Res", "Residential"),
            ("SME", "SME"),
            ("Com", "Commercial"),
            ("Ind", "Industrial"),
        ]

    def extract(self, output_dir: Path) -> None:
        """Extract raw EMI Electrification data to local raw storage."""
        print(f"\n{'=' * 80}")
        print("ELECTRIFICATION DATA: Extract Raw Data")
        print(f"{'=' * 80}")

        output_dir.mkdir(parents=True, exist_ok=True)
        file_manifest = []

        for i, (segment_code, segment_label) in enumerate(
            self.market_segments, start=1
        ):
            print(
                f"\n[{i}/{len(self.market_segments)}] Downloading {segment_label} data..."
            )

            # Create API client with specific parameters
            api = EMIRetailAPI(
                report_id="GUEHMT",
                DateFrom="20130901",
                DateTo="20250930",
                RegionType="NWK_REPORTING_REGION_DIST",
                MarketSegment=segment_code,
                FuelType="All_Drilldown",
            )

            # Fetch data using the API client
            filename = f"{segment_label.lower()}_electrification_raw.csv"
            output_path = output_dir / filename

            # Fetch and parse CSV (skipping header rows as before)
            response_content = api.fetch_data()
            df = pd.read_csv(BytesIO(response_content), skiprows=12)

            # Save to file
            df.to_csv(output_path, index=False)
            file_manifest.append(filename)
            print(f"      ✓ Saved: {filename} ({len(df)} rows)")

        # Save manifest
        manifest_path = output_dir / "_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump({"files": file_manifest}, f, indent=2)
        print(f"\n✓ Manifest saved with {len(file_manifest)} files")

        print(f"\n{'=' * 80}")
        print(f"✓ Extraction complete: {output_dir}")
        print(f"{'=' * 80}\n")


def main():
    """Main function to run the extraction pipeline."""
    settings = get_settings()

    # Define output directory in raw storage
    output_dir = settings.raw_dir / "emi_battery_solar"

    # Create extractor
    extractor = EMIBatterySolarExtractor()

    # Run the extraction process
    try:
        extractor.extract(output_dir=output_dir)
    except Exception as e:
        print(f"\n✗ Extraction failed: {e}")
        raise


if __name__ == "__main__":
    main()
