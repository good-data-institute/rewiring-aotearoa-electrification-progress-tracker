"""Extract: EMI Electricity Generation data pipeline.

This script handles raw data extraction:
1. Extracts raw CSV files from EMI Azure Blob Storage (multiple files)
2. Saves raw data exactly as received (no cleaning/transformation)
3. Also fetches POC-to-Region concordance data
"""

from pathlib import Path
import json

from etl.apis.emi import EMIGenerationAPI
from etl.core.config import get_settings


class EMIGenerationExtractor:
    """Data extractor for EMI Generation: Extract from Azure Blob to raw storage."""

    def __init__(
        self,
        year_from: int = 2020,
        year_to: int = 2025,
    ):
        """Initialize extractor with date range parameters.

        Args:
            year_from: Start year for data extraction
            year_to: End year for data extraction
        """
        self.api = EMIGenerationAPI(year_from=year_from, year_to=year_to)

    def extract(self, output_dir: Path) -> None:
        """Extract raw data from Azure Blob Storage.

        Args:
            output_dir: Directory to save raw CSV files
        """
        print(f"\n{'='*80}")
        print("EMI ELECTRICITY GENERATION: Extract Raw Data")
        print(f"{'='*80}")

        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Extract generation data files
        print("\n[1/2] Extracting generation data from EMI Azure Blob Storage...")
        print(
            f"      Year range: {self.api.params.year_from}-{self.api.params.year_to}"
        )

        csv_files = self.api.fetch_generation_data()

        file_manifest = []
        for blob_name, data_stream in csv_files:
            # Extract filename from blob path
            filename = Path(blob_name).name
            output_path = output_dir / filename

            # Save raw CSV file
            with open(output_path, "wb") as f:
                f.write(data_stream.read())

            file_manifest.append(filename)
            print(f"      ✓ Saved: {filename}")

        # Save manifest of files
        manifest_path = output_dir / "_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(
                {
                    "year_from": self.api.params.year_from,
                    "year_to": self.api.params.year_to,
                    "files": file_manifest,
                },
                f,
                indent=2,
            )
        print(f"      ✓ Saved manifest: _manifest.json ({len(file_manifest)} files)")

        # Step 2: Extract concordance data
        print("\n[2/2] Extracting POC-to-Region concordance...")
        concordance_data = self.api.fetch_concordance()

        concordance_path = output_dir / "poc_region_concordance.csv"
        with open(concordance_path, "wb") as f:
            f.write(concordance_data)

        print("      ✓ Saved: poc_region_concordance.csv")

        print(f"\n{'='*80}")
        print(f"✓ Extraction complete: {output_dir}")
        print(f"  Files extracted: {len(file_manifest)}")
        print(f"{'='*80}\n")


def main():
    """Main function to run the extraction pipeline."""
    settings = get_settings()

    # Define output directory in raw storage
    output_dir = settings.raw_dir / "emi_generation"

    # Create extractor with year range
    extractor = EMIGenerationExtractor(
        year_from=2020,
        year_to=2025,
    )

    # Run the extraction process
    try:
        extractor.extract(output_dir=output_dir)
    except Exception as e:
        print(f"\n✗ Extraction failed: {e}")
        raise


if __name__ == "__main__":
    main()
