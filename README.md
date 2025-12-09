# ⚡ Rewiring Aotearoa Electrification Progress Tracker

A data engineering project for tracking electrification progress in Aotearoa New Zealand using electricity market data by:
- Ingesting raw data from multiple energy sources (EMI, EECA, GIC)
- Processing and transforming data through layered architecture
- Serving analytics via REST API with DuckDB querying
- Visualizing data in interactive dashboards

Key features:
- **Layered Data Architecture**: Raw → Processed → Metrics data flow
- **Split ETL Pipelines**: Separate extract and transform steps
- **DuckDB Backend**: Efficient querying with repository pattern
- **Multiple Data Sources**: EMI Generation, EECA Energy, GIC Gas
- **REST API**: FastAPI backend with filtering and query support
- **Dual Dashboards**: Streamlit and Shiny for Python options
- **Type Safety**: Pydantic validation throughout
- **Code Quality**: Pre-commit hooks with Ruff

## 📋 Prerequisites

- **uv** - Fast Python package manager ([install guide](https://docs.astral.sh/uv/))

### Installing uv

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 🚀 Quick Start

### 1. Clone and Setup

**Windows:**
```powershell
git clone https://github.com/good-data-institute/rewiring-aotearoa-electrification-progress-tracker.git
cd rewiring-aotearoa-electrification-progress-tracker
uv venv --python 3.12
.venv\Scripts\Activate.ps1
uv sync
pre-commit install
Copy-Item .env.example .env
```

**macOS/Linux:**
```bash
git clone https://github.com/good-data-institute/rewiring-aotearoa-electrification-progress-tracker.git
cd rewiring-aotearoa-electrification-progress-tracker
uv venv --python 3.12
source .venv/bin/activate
uv sync
pre-commit install
cp .env.example .env
```

### 2. Run ETL Pipelines

**Extract raw data:**
```bash
# EECA Energy
python -m etl.pipelines.eeca.extract

# GIC Gas
python -m etl.pipelines.gic.extract

# EMI Generation
python -m etl.pipelines.emi_generation.extract
```

**Transform to processed:**
```bash
python -m etl.pipelines.eeca.transform
python -m etl.pipelines.gic.transform
python -m etl.pipelines.emi_generation.transform
```

**Create metrics/analytics:**
```bash
python -m etl.pipelines.emi_demo.process_demo
# Add other analytics as needed
```

### 3. Run Backend and Dashboards

**Terminal 1 - Backend:**
```bash
python -m backend.main
```

**Terminal 2 - Dashboard:**
```bash
streamlit run frontend/Introduction.py
shiny run frontend/shiny_app.py --port 8502
```

🎉 Done! The following URLs should work now:

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Streamlit: http://localhost:8501
- Shiny: http://localhost:8502

## 🔧 Development

### Code Quality
```bash
ruff check --fix .        # Lint and fix
ruff format .             # Format code
pre-commit run --all-files # Run all checks
```

### Dependencies
```bash
uv add package-name             # Add dependency
uv add --dev package-name       # Add dev dependency
uv remove package-name          # Remove dependency
uv sync --upgrade               # Install dependencies into the current environment
uv pip list                     # List packages
```

### Testing
```bash
pytest                    # Run tests
```

## 📊 Key Concepts

### Three-Layer Data Architecture
1. **Raw Layer** (`data/raw/`): Original data exactly as received from APIs
2. **Processed Layer** (`data/processed/`): Cleaned, validated, standardized data
3. **Metrics Layer** (`data/metrics/`): Business-ready analytics and aggregations

### Split ETL Pipeline
Each data source has separate scripts:
- **`extract.py`**: Fetch raw data from API → save to `data/raw/`
- **`transform.py`**: Read raw data → clean/transform → save to `data/processed/`
- **`analytics.py`**: Read processed data → aggregate/analyze → save to `data/metrics/`

### Backend Architecture
- **DuckDB Repository Pattern**: Efficient SQL querying of CSV data
- **RESTful API**: FastAPI endpoints for both processed and metrics layers
- **Query Support**: Filter by date ranges, columns, with pagination
- **Decoupled Design**: Frontend only communicates through API

### Data Sources
1. **EMI Generation**: Electricity generation by fuel type
2. **EMI Solar and Battery**: Count and capacity of installed solar and battery infrastucture
2. **EECA**: Energy end-use by fuel type
3. **GIC**: Gas connection statistics
