# ETL Pipeline Implementation Summary

## Overview

This document summarizes the APIs and ETL pipelines created for the four data sources identified in the sample folder, following the established 2-layer architecture pattern (processed → analytics).

## Architecture

- **2-Layer Design**: Follows the existing pattern with `processed` (extract + transform) and `analytics` (aggregations) layers
- **Dynamic Parameters**: All APIs and pipelines support configurable date ranges
- **Output Format**: CSV files for all layers
- **Blob Storage**: Azure Blob Storage access integrated into EMI Generation API

## Data Sources & Implementation

### 1. EECA Energy Consumption (Energy End Use Database)

**Source**: Energy Efficiency and Conservation Authority (EECA)
- URL: `https://www.eeca.govt.nz/assets/EECA-Resources/Research-papers-guides/EEUD-Data-2017-2023.xlsx`
- Format: Excel file with energy consumption by sector and fuel type

**Files Created**:
- API: `etl/apis/eeca.py` - Fetches Excel file from EECA
- Extract/Transform: `etl/pipelines/eeca/extract_transform.py` - Cleans and standardizes data
  - Fuel type mapping (Electricity, Petrol, Diesel, Coal, Wood, Other)
  - Date extraction (year from periodEndDate)
  - Configurable year range filtering
- Analytics: `etl/pipelines/eeca/analytics.py` - Calculates electricity percentage
  - Computes electricity share of total energy consumption by year
  - Metric: `_13_P1_ElecCons` (percentage)

**Key Features**:
- Optional year_from/year_to filtering
- Standardized fuel categories
- Missing value reporting

---

### 2. GIC Gas Connections (Gas Industry Company)

**Source**: Gas Industry Company (GIC) Registry Statistics
- URL: `https://weblink.blob.core.windows.net/%24web/RegistryStats.xlsx`
- Format: Excel file with two sheets:
  - "By Gas Gate": Gas connection data
  - "Gate Region": Regional concordance

**Files Created**:
- API: `etl/apis/gic.py` - Fetches Excel file from GIC
- Extract/Transform: `etl/pipelines/gic/extract_transform.py` - Processes and enriches data
  - Joins with regional concordance
  - Date extraction (year/month)
  - Filters out invalid gas gate codes
  - Configurable date range filtering
- Analytics: `etl/pipelines/gic/analytics.py` - Aggregates by region and time
  - Monthly new gas connections by region
  - Metric: `_10_P1_Gas` (count of new connections)

**Key Features**:
- Regional mapping from concordance sheet
- Date and month filtering support
- Handles within-pipeline concordance lookup

---

### 3. EMI Electricity Generation

**Source**: Electricity Market Information (EMI) - Azure Blob Storage
- Container: `https://emidatasets.blob.core.windows.net/publicdata`
- Path: `Datasets/Wholesale/Generation/Generation_MD/`
- Format: Multiple CSV files (one per month, 2020-2025)
- Concordance: POC to Region mapping from EMI API

**Files Created**:
- API: `etl/apis/emi_generation.py` - Azure Blob Storage client
  - Scans blob container for Generation_MD CSV files
  - Filters by year range
  - Fetches POC-to-Region concordance data
  - Custom implementation (not using BaseAPIClient due to blob storage)
- Extract/Transform: `etl/pipelines/emi_generation/extract_transform.py` - Processes generation data
  - Concatenates multiple CSV files
  - Joins with POC-to-Region concordance
  - Classifies renewable vs non-renewable fuel types
  - Sums trading periods (TP1-TP48) into total kWh
  - Drops trading period columns to reduce size
  - Configurable year range (year_from, year_to)
- Analytics: `etl/pipelines/emi_generation/analytics.py` - Calculates renewable share
  - Monthly renewable generation percentage by region
  - Metric: `_12_P1_EnergyRenew` (share of renewable generation)

**Key Features**:
- Azure Blob Storage integration with azure-storage-blob library
- Multi-file concatenation
- Regional concordance handling within pipeline
- Renewable fuel classification (Hydro, Wind, Solar, Wood, Geo, etc.)
- Trading period aggregation

---

## File Structure

```
etl/
├── apis/
│   ├── eeca.py              # EECA Energy End Use Database API
│   ├── emi_generation.py    # EMI Generation Azure Blob API
│   ├── emi_retail.py        # (existing)
│   └── gic.py               # GIC Gas Connections API
│
└── pipelines/
    ├── eeca/
    │   ├── __init__.py
    │   ├── extract_transform.py    # Energy consumption processing
    │   └── analytics.py            # Electricity percentage calculation
    │
    ├── emi/
    │   └── (existing EMI retail pipeline)
    │
    ├── emi_generation/
    │   ├── __init__.py
    │   ├── extract_transform.py    # Generation data processing
    │   └── analytics.py            # Renewable share calculation
    │
    └── gic/
        ├── __init__.py
        ├── extract_transform.py    # Gas connections processing
        └── analytics.py            # Regional aggregation
```

## Data Flow

### EECA Energy Consumption
```
Excel API → extract_transform.py → data/processed/eeca/eeca_energy_consumption_cleaned.csv
                                 ↓
                          analytics.py → data/analytics/eeca/eeca_electricity_percentage.csv
```

### GIC Gas Connections
```
Excel API → extract_transform.py → data/processed/gic/gic_gas_connections_cleaned.csv
                                 ↓
                          analytics.py → data/analytics/gic/gic_gas_connections_analytics.csv
```

### EMI Generation
```
Azure Blob → extract_transform.py → data/processed/emi_generation/emi_generation_cleaned.csv
                                  ↓
                           analytics.py → data/analytics/emi_generation/emi_generation_analytics.csv
```

## Dependencies Added

Updated `pyproject.toml` with required packages:
- `azure-storage-blob>=12.24.0` - For Azure Blob Storage access
- `openpyxl>=3.1.0` - For Excel file reading
- `python-dotenv>=1.0.0` - For environment configuration (already in use)
- `requests>=2.32.0` - For HTTP requests (already in use)

## Usage Examples

### EECA Energy Consumption
```python
# Extract & Transform
from etl.pipelines.eeca.extract_transform import EECAEnergyConsumptionProcessor

processor = EECAEnergyConsumptionProcessor(year_from=2017, year_to=2023)
processor.process(input_path=None, output_path=Path("data/processed/eeca/cleaned.csv"))

# Analytics
from etl.pipelines.eeca.analytics import EECAElectricityPercentageAnalytics

analytics = EECAElectricityPercentageAnalytics()
analytics.process(
    input_path=Path("data/processed/eeca/cleaned.csv"),
    output_path=Path("data/analytics/eeca/electricity_pct.csv")
)
```

### GIC Gas Connections
```python
# Extract & Transform
from etl.pipelines.gic.extract_transform import GICGasConnectionsProcessor

processor = GICGasConnectionsProcessor(year_from=2020, year_to=2025)
processor.process(input_path=None, output_path=Path("data/processed/gic/cleaned.csv"))

# Analytics
from etl.pipelines.gic.analytics import GICGasConnectionsAnalytics

analytics = GICGasConnectionsAnalytics()
analytics.process(
    input_path=Path("data/processed/gic/cleaned.csv"),
    output_path=Path("data/analytics/gic/connections.csv")
)
```

### EMI Generation
```python
# Extract & Transform
from etl.pipelines.emi_generation.extract_transform import EMIGenerationProcessor

processor = EMIGenerationProcessor(year_from=2020, year_to=2025)
processor.process(input_path=None, output_path=Path("data/processed/emi_generation/cleaned.csv"))

# Analytics
from etl.pipelines.emi_generation.analytics import EMIGenerationAnalytics

analytics = EMIGenerationAnalytics()
analytics.process(
    input_path=Path("data/processed/emi_generation/cleaned.csv"),
    output_path=Path("data/analytics/emi_generation/renewable_share.csv")
)
```

## Key Design Decisions

1. **2-Layer Architecture**: Followed existing pattern with processed and analytics layers
2. **CSV Output**: All layers output CSV format for consistency
3. **Azure Blob in API Layer**: Azure Blob Storage access kept in API layer as requested
4. **Dynamic Date Ranges**: All pipelines support configurable date filtering
5. **Concordance Handling**: Regional/lookup tables handled within pipeline logic
6. **Excel to Pandas**: Excel files loaded directly into pandas and saved as CSV
7. **Separate Folders**: Each data source has its own folder in apis/ and pipelines/

## Metrics Generated

| Data Source | Metric Code | Description |
|-------------|-------------|-------------|
| EECA | `_13_P1_ElecCons` | Electricity % of total energy consumption |
| EECA | `_14_P1_EnergyxFuel` | Energy consumption by fuel type (MWh) |
| GIC | `_10_P1_Gas` | New gas connections by region |
| EMI Generation | `_12_P1_EnergyRenew` | Renewable share of generation |

## Next Steps

1. Install dependencies: `uv pip install -e .` or `pip install -e .`
2. Test each pipeline individually using the `main()` functions
3. Create orchestration scripts to run all pipelines in sequence
4. Integrate with existing dashboard/frontend applications
5. Add error handling and logging as needed
6. Consider adding data quality checks and validation

## Testing

Each pipeline can be tested independently:

```powershell
# EECA Energy Consumption
python -m etl.pipelines.eeca.extract_transform
python -m etl.pipelines.eeca.analytics

# GIC Gas Connections
python -m etl.pipelines.gic.extract_transform
python -m etl.pipelines.gic.analytics

# EMI Generation
python -m etl.pipelines.emi_generation.extract_transform
python -m etl.pipelines.emi_generation.analytics
```
