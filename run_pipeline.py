"""Run the complete ETL pipeline from bronze to gold.

This script executes all three layers of the medallion architecture in sequence.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from etl.pipelines import bronze_emi_retail, silver_emi_retail, gold_emi_retail


def main():
    """Execute the complete ETL pipeline."""
    print("=" * 80)
    print("COMPLETE ETL PIPELINE EXECUTION")
    print("=" * 80)
    print("\nThis script will run:")
    print("1. Bronze layer: Ingest raw data from API")
    print("2. Silver layer: Clean and validate data")
    print("3. Gold layer: Create business-ready aggregations")
    print("\n" + "=" * 80)

    try:
        # Bronze layer
        print("\n[1/3] BRONZE LAYER")
        print("-" * 80)
        bronze_emi_retail.main()

        # Silver layer
        print("\n[2/3] SILVER LAYER")
        print("-" * 80)
        silver_emi_retail.main()

        # Gold layer
        print("\n[3/3] GOLD LAYER")
        print("-" * 80)
        gold_emi_retail.main()

        # Success summary
        print("\n" + "=" * 80)
        print("✓ COMPLETE ETL PIPELINE FINISHED SUCCESSFULLY")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Start the backend: python -m backend.main")
        print("2. Launch a dashboard:")
        print("   - Streamlit: streamlit run frontend/streamlit_app.py")
        print("   - Shiny: shiny run frontend/shiny_app.py --port 8502")

    except Exception as e:
        print("\n" + "=" * 80)
        print("✗ ETL PIPELINE FAILED")
        print("=" * 80)
        print(f"\nError: {e}")
        print("\nPlease check the error message above and resolve any issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()
