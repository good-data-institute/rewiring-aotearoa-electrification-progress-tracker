"""Extract: Waka Kotahi Motor Vehicle Register data pipeline.

This script handles raw data extraction:
1. Extracts raw CSV data from Waka Kotahi Open Data Portal
2. Saves raw data to Parquet format (optimized for large datasets)
3. Uses streaming to handle large file sizes efficiently
"""

from io import BytesIO
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from etl.apis.waka_kotahi_mvr import WakaKotahiMVRAPI
from etl.core.config import get_settings


class WakaKotahiMVRExtractor:
    """Data extractor for Waka Kotahi Motor Vehicle Register.

    Downloads complete MVR dataset from the open data portal and saves
    as raw Parquet for efficient storage and processing.
    """

    def __init__(self, chunk_size: int = 500_000):
        """Initialize extractor with API client and streaming parameters.

        Args:
            chunk_size: Number of rows to process at once (balance speed vs memory)
        """
        self.api = WakaKotahiMVRAPI()
        self.chunk_size = chunk_size

    def extract(self, output_path: Path) -> None:
        """Extract raw data from Waka Kotahi Open Data Portal.

        Uses streaming to handle large CSV files efficiently, writing
        directly to Parquet format for optimized storage.

        Args:
            output_path: Path to save raw Parquet file
        """
        print(f"\n{'='*80}")
        print("WAKA KOTAHI MOTOR VEHICLE REGISTER: Extract Raw Data")
        print(f"{'='*80}")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print("\n[1/2] Fetching CSV data from Waka Kotahi Open Data Portal...")
        print(f"      URL: {self.api.params.url[:80]}...")

        # Step 1: Fetch CSV data using API client
        # Note: For large files, we get the raw response and stream it
        import requests

        response = requests.get(self.api.params.url, stream=True, timeout=60)
        response.raise_for_status()

        # Step 2: Process in chunks and write to Parquet
        print(f"\n[2/2] Processing data in chunks of {self.chunk_size:,} rows...")

        first_chunk = True
        parquet_writer = None
        total_rows = 0

        for chunk in pd.read_csv(
            BytesIO(response.content),
            compression="zip",
            chunksize=self.chunk_size,
            dtype=str,  # Keep all as string for raw layer
        ):
            # Convert to PyArrow Table
            table = pa.Table.from_pandas(chunk, preserve_index=False)

            # Initialize or append to Parquet
            if first_chunk:
                parquet_writer = pq.ParquetWriter(
                    output_path, table.schema, compression="snappy"
                )
                first_chunk = False

            parquet_writer.write_table(table)
            total_rows += len(chunk)
            print(
                f"      ✓ Processed chunk with {len(chunk):,} rows (total: {total_rows:,})"
            )

        # Close writer
        if parquet_writer:
            parquet_writer.close()

        print(f"\n{'='*80}")
        print(f"✓ Extraction complete: {output_path}")
        print(f"  Total rows extracted: {total_rows:,}")
        print(f"{'='*80}\n")


def main():
    """Main function to run the extraction pipeline."""
    settings = get_settings()

    # Define output path in raw directory
    output_path = settings.raw_dir / "waka_kotahi_mvr" / "mvr_raw.parquet"

    # Create extractor
    extractor = WakaKotahiMVRExtractor()

    # Run the extraction process
    try:
        extractor.extract(output_path=output_path)
    except Exception as e:
        print(f"\n✗ Extraction failed: {e}")
        raise


if __name__ == "__main__":
    main()
