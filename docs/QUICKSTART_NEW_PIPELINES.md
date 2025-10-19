# Quick Start Guide - New ETL Pipelines

## Installation

First, install the required dependencies:

```powershell
# Install dependencies (if using uv)
uv pip install -e .

# OR if using pip
pip install -e .
```

This will install:
- `azure-storage-blob` - For EMI Generation Azure Blob access
- `openpyxl` - For EECA and GIC Excel file reading
- All other existing dependencies

## Running Individual Pipelines

### 1. EECA Energy Consumption

#### Extract & Transform (Processed Layer)
```powershell
python -m etl.pipelines.eeca.extract_transform
```
- **Input**: EECA Excel file (fetched from API)
- **Output**: `data/processed/eeca/eeca_energy_consumption_cleaned.csv`
- **Configurable Parameters**: `year_from`, `year_to`

#### Analytics Layer
```powershell
python -m etl.pipelines.eeca.analytics
```
- **Input**: `data/processed/eeca/eeca_energy_consumption_cleaned.csv`
- **Output**: `data/analytics/eeca/eeca_electricity_percentage.csv`
- **Metric**: Electricity % of total energy consumption

---

### 2. GIC Gas Connections

#### Extract & Transform (Processed Layer)
```powershell
python -m etl.pipelines.gic.extract_transform
```
- **Input**: GIC Excel file (fetched from API)
- **Output**: `data/processed/gic/gic_gas_connections_cleaned.csv`
- **Configurable Parameters**: `year_from`, `year_to`, `month_from`, `month_to`

#### Analytics Layer
```powershell
python -m etl.pipelines.gic.analytics
```
- **Input**: `data/processed/gic/gic_gas_connections_cleaned.csv`
- **Output**: `data/analytics/gic/gic_gas_connections_analytics.csv`
- **Metric**: Monthly new gas connections by region

---

### 3. EMI Electricity Generation

#### Extract & Transform (Processed Layer)
```powershell
python -m etl.pipelines.emi_generation.extract_transform
```
- **Input**: EMI Azure Blob Storage (multiple CSV files)
- **Output**: `data/processed/emi_generation/emi_generation_cleaned.csv`
- **Configurable Parameters**: `year_from`, `year_to`
- **Note**: This will download multiple CSV files from Azure Blob Storage

#### Analytics Layer
```powershell
python -m etl.pipelines.emi_generation.analytics
```
- **Input**: `data/processed/emi_generation/emi_generation_cleaned.csv`
- **Output**: `data/analytics/emi_generation/emi_generation_analytics.csv`
- **Metric**: Monthly renewable generation share by region

---

## Customizing Date Ranges

### Example: EECA with custom years
```python
from pathlib import Path
from etl.pipelines.eeca.extract_transform import EECAEnergyConsumptionProcessor

processor = EECAEnergyConsumptionProcessor(
    year_from=2018,  # Start from 2018
    year_to=2022,    # End at 2022
)
processor.process(
    input_path=None,
    output_path=Path("data/processed/eeca/eeca_energy_consumption_cleaned.csv")
)
```

### Example: GIC with custom date range
```python
from pathlib import Path
from etl.pipelines.gic.extract_transform import GICGasConnectionsProcessor

processor = GICGasConnectionsProcessor(
    year_from=2020,
    year_to=2023,
    month_from=1,   # Start from January
    month_to=6,     # End at June
)
processor.process(
    input_path=None,
    output_path=Path("data/processed/gic/gic_gas_connections_cleaned.csv")
)
```

### Example: EMI Generation with custom years
```python
from pathlib import Path
from etl.pipelines.emi_generation.extract_transform import EMIGenerationProcessor

processor = EMIGenerationProcessor(
    year_from=2022,  # Only 2022-2024
    year_to=2024,
)
processor.process(
    input_path=None,
    output_path=Path("data/processed/emi_generation/emi_generation_cleaned.csv")
)
```

---

## Running All Pipelines Sequentially

You can create a master script to run all pipelines:

```python
# run_all_pipelines.py
from etl.pipelines.eeca.extract_transform import EECAEnergyConsumptionProcessor
from etl.pipelines.eeca.analytics import EECAElectricityPercentageAnalytics
from etl.pipelines.gic.extract_transform import GICGasConnectionsProcessor
from etl.pipelines.gic.analytics import GICGasConnectionsAnalytics
from etl.pipelines.emi_generation.extract_transform import EMIGenerationProcessor
from etl.pipelines.emi_generation.analytics import EMIGenerationAnalytics
from etl.core.config import get_settings
from pathlib import Path

def main():
    settings = get_settings()

    print("="*80)
    print("RUNNING ALL ETL PIPELINES")
    print("="*80)

    # EECA Energy Consumption
    print("\n1. EECA Energy Consumption...")
    eeca_processor = EECAEnergyConsumptionProcessor(year_from=2017, year_to=2023)
    eeca_processor.process(
        input_path=None,
        output_path=settings.processed_dir / "eeca" / "eeca_energy_consumption_cleaned.csv"
    )

    eeca_analytics = EECAElectricityPercentageAnalytics()
    eeca_analytics.process(
        input_path=settings.processed_dir / "eeca" / "eeca_energy_consumption_cleaned.csv",
        output_path=settings.analytics_dir / "eeca" / "eeca_electricity_percentage.csv"
    )

    # GIC Gas Connections
    print("\n2. GIC Gas Connections...")
    gic_processor = GICGasConnectionsProcessor()
    gic_processor.process(
        input_path=None,
        output_path=settings.processed_dir / "gic" / "gic_gas_connections_cleaned.csv"
    )

    gic_analytics = GICGasConnectionsAnalytics()
    gic_analytics.process(
        input_path=settings.processed_dir / "gic" / "gic_gas_connections_cleaned.csv",
        output_path=settings.analytics_dir / "gic" / "gic_gas_connections_analytics.csv"
    )

    # EMI Generation
    print("\n3. EMI Electricity Generation...")
    emi_processor = EMIGenerationProcessor(year_from=2020, year_to=2025)
    emi_processor.process(
        input_path=None,
        output_path=settings.processed_dir / "emi_generation" / "emi_generation_cleaned.csv"
    )

    emi_analytics = EMIGenerationAnalytics()
    emi_analytics.process(
        input_path=settings.processed_dir / "emi_generation" / "emi_generation_cleaned.csv",
        output_path=settings.analytics_dir / "emi_generation" / "emi_generation_analytics.csv"
    )

    print("\n" + "="*80)
    print("ALL PIPELINES COMPLETED SUCCESSFULLY!")
    print("="*80)

if __name__ == "__main__":
    main()
```

Run with:
```powershell
python run_all_pipelines.py
```

---

## Expected Output Structure

After running all pipelines, you'll have:

```
data/
├── processed/
│   ├── eeca/
│   │   └── eeca_energy_consumption_cleaned.csv
│   ├── gic/
│   │   └── gic_gas_connections_cleaned.csv
│   └── emi_generation/
│       └── emi_generation_cleaned.csv
│
└── analytics/
    ├── eeca/
    │   └── eeca_electricity_percentage.csv
    ├── gic/
    │   └── gic_gas_connections_analytics.csv
    └── emi_generation/
        └── emi_generation_analytics.csv
```

---

## Troubleshooting

### Azure Blob Storage Issues
If you get connection errors with EMI Generation:
- Check internet connectivity
- Verify the Azure Blob container URL is accessible
- The container is public, so no authentication is needed

### Excel File Issues
If EECA or GIC pipelines fail:
- Ensure `openpyxl` is installed: `pip install openpyxl`
- Check the URL is accessible
- Verify the sheet names in the API configuration

### Memory Issues
For large datasets (especially EMI Generation):
- Process smaller year ranges
- Increase Python heap size if needed
- Consider using DuckDB for transformations (already available in base classes)

---

## Next Steps

1. **Test each pipeline individually** to ensure they work
2. **Integrate with existing dashboards** (Streamlit/Shiny apps)
3. **Set up scheduled runs** (cron jobs, Task Scheduler, etc.)
4. **Add data quality checks** before and after processing
5. **Create monitoring and alerting** for pipeline failures
6. **Optimize performance** if processing times are too long

For more details, see `docs/ETL_IMPLEMENTATION_SUMMARY.md`
