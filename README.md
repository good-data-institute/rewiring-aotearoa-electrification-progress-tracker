# ⚡ Rewiring Aotearoa Electrification Progress Tracker

A minimal data engineering project for tracking electrification progress in Aotearoa New Zealand using electricity market data by:
- Ingesting and processing data from multiple energy sources (EECA, GIC, EMI)
- Serving analytics via REST API
- Visualizing data in interactive dashboards

Key features:
- **Dual ETL Approach**: Use DuckDB SQL and/or Pandas Python for transformations
- **Multiple Data Sources**: EMI, EECA Energy, GIC
- **REST API**: FastAPI backend serving processed data
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

### 2. Run Everything

**Terminal 1 - Backend:**
```bash
python -m backend.main
```

**Terminal 2 - Dashboard:**
```bash
streamlit run frontend/streamlit_app.py
shiny run frontend/shiny_app.py --port 8502
```

🎉 Done! The following URL should work now:

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

### Layered Architecture
- **Processed**: Cleaned, validated data from APIs → `data/processed/`
- **Metrics**: Business-ready analytics → `data/metrics/`

### Dual ETL Approach
Write transformations using **DuckDB SQL** or **Pandas Python**:

See **[ETL_GUIDE.md](etl/ETL_GUIDE.md)** for comprehensive patterns and examples.

### Data Sources
1. **EMI Retail**: Electricity consumption data
2. **EECA**: Energy end-use by fuel type
3. **GIC**: Gas connection statistics
4. **EMI Generation**: Electricity generation by fuel type

See **[ETL_IMPLEMENTATION_SUMMARY.md](docs/ETL_IMPLEMENTATION_SUMMARY.md)** for implementation details.
