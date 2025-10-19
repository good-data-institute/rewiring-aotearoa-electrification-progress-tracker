# Quick Start - New Pipeline Recipes

## Running Individual Pipelines

### EECA Energy Consumption

**Extract & Transform:**
```powershell
python -m etl.pipelines.eeca.extract_transform
```
- Input: EECA Excel file (API fetched)
- Output: `data/processed/eeca/eeca_energy_consumption_cleaned.csv`

**Analytics:**
```powershell
python -m etl.pipelines.eeca.analytics
```
- Input: Cleaned data
- Output: `data/analytics/eeca/eeca_electricity_percentage.csv`
- Metric: `_13_P1_ElecCons` (Electricity % of total energy)

---

### GIC Gas Connections

**Extract & Transform:**
```powershell
python -m etl.pipelines.gic.extract_transform
```
- Input: GIC Excel file (API fetched)
- Output: `data/processed/gic/gic_gas_connections_cleaned.csv`

**Analytics:**
```powershell
python -m etl.pipelines.gic.analytics
```
- Input: Cleaned data
- Output: `data/analytics/gic/gic_gas_connections_analytics.csv`
- Metric: `_10_P1_Gas` (Monthly new connections by region)

---

### EMI Electricity Generation

**Extract & Transform:**
```powershell
python -m etl.pipelines.emi_generation.extract_transform
```
- Input: EMI Azure Blob Storage CSVs
- Output: `data/processed/emi_generation/emi_generation_cleaned.csv`
- Note: Downloads multiple CSV files

**Analytics:**
```powershell
python -m etl.pipelines.emi_generation.analytics
```
- Input: Cleaned data
- Output: `data/analytics/emi_generation/emi_generation_analytics.csv`
- Metric: `_12_P1_EnergyRenew` (Renewable generation share)

---

## Customizing Date Ranges

### EECA - Custom Years
```python
from pathlib import Path
from etl.pipelines.eeca.extract_transform import EECAEnergyConsumptionProcessor

processor = EECAEnergyConsumptionProcessor(
    year_from=2018,
    year_to=2022,
)
processor.process(
    input_path=None,
    output_path=Path("data/processed/eeca/eeca_energy_consumption_cleaned.csv")
)
```

### GIC - Custom Date Range
```python
from pathlib import Path
from etl.pipelines.gic.extract_transform import GICGasConnectionsProcessor

processor = GICGasConnectionsProcessor(
    year_from=2020,
    year_to=2023,
    month_from=1,
    month_to=6,
)
processor.process(
    input_path=None,
    output_path=Path("data/processed/gic/gic_gas_connections_cleaned.csv")
)
```

### EMI Generation - Custom Years
```python
from pathlib import Path
from etl.pipelines.emi_generation.extract_transform import EMIGenerationProcessor

processor = EMIGenerationProcessor(
    year_from=2022,
    year_to=2024,
)
processor.process(
    input_path=None,
    output_path=Path("data/processed/emi_generation/emi_generation_cleaned.csv")
)
```

---

## Master Script - Run All Pipelines

Create `run_all_pipelines.py`:

```python
from etl.pipelines.eeca.extract_transform import EECAEnergyConsumptionProcessor
from etl.pipelines.eeca.analytics import EECAElectricityPercentageAnalytics
from etl.pipelines.gic.extract_transform import GICGasConnectionsProcessor
from etl.pipelines.gic.analytics import GICGasConnectionsAnalytics
from etl.pipelines.emi_generation.extract_transform import EMIGenerationProcessor
from etl.pipelines.emi_generation.analytics import EMIGenerationAnalytics
from etl.core.config import get_settings

def main():
    settings = get_settings()

    # EECA
    print("Running EECA...")
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

    # GIC
    print("Running GIC...")
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
    print("Running EMI Generation...")
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

    print("All pipelines completed!")

if __name__ == "__main__":
    main()
```

Run:
```bash
python run_all_pipelines.py
```

## Expected Output

```
data/
├── processed/
│   ├── eeca/eeca_energy_consumption_cleaned.csv
│   ├── gic/gic_gas_connections_cleaned.csv
│   └── emi_generation/emi_generation_cleaned.csv
└── analytics/
    ├── eeca/eeca_electricity_percentage.csv
    ├── gic/gic_gas_connections_analytics.csv
    └── emi_generation/emi_generation_analytics.csv
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Azure Blob errors** | Check internet connection; container is public |
| **Excel file errors** | Ensure `openpyxl` installed: `uv add openpyxl` |
| **Memory issues** | Process smaller year ranges |
