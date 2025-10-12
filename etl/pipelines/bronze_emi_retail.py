"""Bronze layer ETL: Ingest raw data from EMI Retail API.

This script fetches raw electricity market data from the EMI Retail API
and stores it in the bronze layer (raw data storage).
"""

from etl.apis.emi_retail import EMIRetailAPI
from etl.core.config import get_settings


def main():
    """Main ETL function for bronze layer ingestion."""
    print("=" * 80)
    print("BRONZE LAYER ETL: EMI Retail Data Ingestion")
    print("=" * 80)

    settings = get_settings()

    # Initialize API client with default parameters
    # You can customize these parameters as needed
    api = EMIRetailAPI(
        report_id="GUEHMT",
        Capacity="All_Drilldown",
        DateFrom="20250801",
        DateTo="20250831",
        RegionType="NZ",
        FuelType="All_Drilldown",
        # _rsdr="ALL",
        # _si="v|4",
    )

    # Define output path in bronze layer
    output_filename = api.get_default_output_filename()
    output_path = settings.bronze_dir / "emi_retail" / output_filename

    print(f"\nOutput path: {output_path}")
    print(f"Fetching data with parameters: {api.params.model_dump()}\n")

    # Fetch and save data
    try:
        api.fetch_data(output_path=output_path)
        print("\n✓ Bronze layer ingestion completed successfully")
        print(f"✓ Data saved to: {output_path}")
    except Exception as e:
        print(f"\n✗ Bronze layer ingestion failed: {e}")
        raise


if __name__ == "__main__":
    main()
