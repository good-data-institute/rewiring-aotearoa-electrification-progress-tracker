# ⚡ Rewiring Aotearoa Electrification Progress Tracker

A minimal data engineering project for tracking electrification progress in Aotearoa New Zealand using electricity market data from the EMI Retail portal.

## 🏗️ Architecture

This project implements a modern data engineering stack with:

- **ETL Pipeline**: Medallion architecture (Bronze → Silver → Gold) with extensible API clients
- **Backend**: FastAPI serving processed data
- **Frontend**: Streamlit and Shiny for Python dashboards
- **Data Processing**: **DuckDB SQL and Pandas Python** - maintainers can define ETL using SQL and/or Python
- **Validation**: Pydantic for schema and API parameter validation
- **Quality**: Pre-commit hooks with Ruff for linting and formatting

### 🔑 Key Feature: SQL + Python ETL

Maintainers can write ETL transformations using **both DuckDB SQL and Pandas Python**:

```python
# Use SQL for data shaping
query = """
SELECT region, DATE_TRUNC('month', date) as month,
       SUM(consumption) as total
FROM read_csv_auto('data/silver/file.csv')
GROUP BY region, month
"""
df = self.execute_duckdb_query(query)

# Then use Pandas for business logic
df['category'] = df['total'].apply(lambda x: 'High' if x > 1000 else 'Low')
```

See [ETL_SQL_PYTHON_GUIDE.md](ETL_SQL_PYTHON_GUIDE.md) and [etl/SQL_EXAMPLES.py](etl/SQL_EXAMPLES.py) for comprehensive examples.

### Project Structure

```
rewiring-aotearoa-electrification-progress-tracker/
├── backend/              # FastAPI backend
│   └── main.py          # API endpoints for serving gold layer data
├── etl/                 # ETL pipeline
│   ├── apis/           # API clients with Pydantic validation
│   │   └── emi_retail.py
│   ├── core/           # Core components
│   │   ├── base_api.py      # Base API client class
│   │   ├── config.py        # Settings management
│   │   └── medallion.py     # Bronze/Silver/Gold layer classes
│   ├── pipelines/      # ETL scripts
│   │   ├── bronze_emi_retail.py   # Raw data ingestion
│   │   ├── silver_emi_retail.py   # Data cleaning
│   │   └── gold_emi_retail.py     # Business-ready aggregations
│   └── SQL_EXAMPLES.py         # SQL query examples for ETL
├── frontend/            # Dashboard applications
│   ├── streamlit_app.py
│   └── shiny_app.py
├── data/               # Data storage (gitignored)
│   ├── bronze/        # Raw data
│   ├── silver/        # Cleaned data
│   └── gold/          # Business-ready data
├── .env               # Environment configuration
├── .env.example       # Example configuration
├── .gitignore         # Git ignore rules
├── .pre-commit-config.yaml  # Pre-commit hooks
├── pyproject.toml     # Project dependencies and configuration
├── README.md          # This file
├── QUICKSTART.md      # Quick reference guide
├── ETL_SQL_PYTHON_GUIDE.md  # Guide for SQL and Python in ETL
└── run_pipeline.py    # Complete pipeline runner
```

## 📋 Prerequisites

- **Python 3.12** or higher
- **uv** - Fast Python package installer and resolver

### Installing uv

#### Windows (PowerShell)

```powershell
# Standalone installer (recommended)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### macOS/Linux

```bash
# Standalone installer (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

See [uv documentation](https://docs.astral.sh/uv/) for more installation options.

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/good-data-institute/rewiring-aotearoa-electrification-progress-tracker.git
cd rewiring-aotearoa-electrification-progress-tracker
```

### 2. Set Up Environment

#### Windows (PowerShell)

```powershell
# Create virtual environment with Python 3.12
uv venv --python 3.12

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Sync dependencies from pyproject.toml
uv sync

# Set up pre-commit hooks
pre-commit install
```

#### macOS/Linux (Bash/Zsh)

```bash
# Create virtual environment with Python 3.12
uv venv --python 3.12

# Activate virtual environment
source .venv/bin/activate

# Sync dependencies from pyproject.toml
uv sync

# Set up pre-commit hooks
pre-commit install
```

### 3. Configure Environment

Copy the example environment file and customize if needed:

#### Windows (PowerShell)

```powershell
Copy-Item .env.example .env
```

#### macOS/Linux

```bash
cp .env.example .env
```

### 4. Run the ETL Pipeline

Execute the medallion architecture pipeline in sequence:

#### Windows (PowerShell)

```powershell
# Bronze: Ingest raw data from API
python -m etl.pipelines.bronze_emi_retail

# Silver: Clean and validate data
python -m etl.pipelines.silver_emi_retail

# Gold: Create business-ready aggregations
python -m etl.pipelines.gold_emi_retail
```

#### macOS/Linux

```bash
# Bronze: Ingest raw data from API
python -m etl.pipelines.bronze_emi_retail

# Silver: Clean and validate data
python -m etl.pipelines.silver_emi_retail

# Gold: Create business-ready aggregations
python -m etl.pipelines.gold_emi_retail
```

### 5. Start the Backend

In a separate terminal:

#### Windows (PowerShell)

```powershell
# Activate virtual environment if not already activated
.venv\Scripts\Activate.ps1

# Start FastAPI backend
python -m backend.main
```

#### macOS/Linux

```bash
# Activate virtual environment if not already activated
source .venv/bin/activate

# Start FastAPI backend
python -m backend.main
```

The API will be available at http://localhost:8000

### 6. Launch a Dashboard

Choose either Streamlit or Shiny for Python:

#### Streamlit

**Windows (PowerShell)**
```powershell
# In another terminal
.venv\Scripts\Activate.ps1
streamlit run frontend/streamlit_app.py
```

**macOS/Linux**
```bash
# In another terminal
source .venv/bin/activate
streamlit run frontend/streamlit_app.py
```

Dashboard will open at http://localhost:8501

#### Shiny for Python

**Windows (PowerShell)**
```powershell
# In another terminal
.venv\Scripts\Activate.ps1
shiny run frontend/shiny_app.py --port 8502
```

**macOS/Linux**
```bash
# In another terminal
source .venv/bin/activate
shiny run frontend/shiny_app.py --port 8502
```

Dashboard will be available at http://localhost:8502

## 🔧 Development

### Code Quality

This project uses Ruff for linting and formatting. Pre-commit hooks are configured to run automatically.

#### Run Linting Manually

```bash
# Check for issues
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Format code
ruff format .
```

#### Run Pre-commit on All Files

```bash
pre-commit run --all-files
```

### Testing

Testing infrastructure is set up but no tests are included yet:

```bash
pytest
```

### Managing Dependencies

Use `uv` commands to manage project dependencies:

```bash
# Add a new dependency
uv add pandas numpy

# Add a dev dependency
uv add --dev pytest ruff

# Remove a dependency
uv remove package-name

# Update all dependencies
uv sync --upgrade

# Show installed packages
uv pip list
```

## 📊 Using the System

### ETL Pipeline with SQL and Python

The ETL pipeline follows the medallion architecture and supports **both DuckDB SQL and Pandas Python** for data transformations:

1. **Bronze Layer** (`bronze_emi_retail.py`):
   - Ingests raw data from EMI Retail API
   - Validates API parameters using Pydantic
   - Stores raw CSV in `data/bronze/`

2. **Silver Layer** (`silver_emi_retail.py`):
   - **Pandas**: Data cleaning, deduplication, column standardization
   - **DuckDB SQL**: Data quality checks and validation queries
   - Example SQL query in code:
     ```sql
     SELECT COUNT(*) as total_rows,
            COUNT(DISTINCT *) as unique_rows
     FROM read_csv_auto('data.csv')
     ```
   - Stores cleaned CSV in `data/silver/`

3. **Gold Layer** (`gold_emi_retail.py`):
   - **DuckDB SQL**: Complex aggregations and analytical queries
   - **Pandas**: Business logic and calculated columns
   - Maintainers can define ETL using either SQL or Python as needed
   - Stores analytics-ready CSV in `data/gold/`

#### Example: Using DuckDB SQL in ETL

```python
# In your silver/gold processor
from etl.core.medallion import SilverLayer

class MyProcessor(SilverLayer):
    def process(self, input_path, output_path):
        # Use SQL for complex queries
        query = """
        SELECT
            date,
            region,
            SUM(consumption) as total_consumption,
            AVG(price) as avg_price
        FROM read_csv_auto('{input_path}')
        WHERE date >= '2020-01-01'
        GROUP BY date, region
        ORDER BY date DESC
        """
        df = self.execute_duckdb_query(query)

        # Continue with Pandas if needed
        df['calculated_field'] = df['total_consumption'] * df['avg_price']

        self.write_csv(df, output_path)
```

### Adding New API Sources

To add a new data source:

1. Create a new API client in `etl/apis/`:

```python
# etl/apis/new_source.py
from typing import Literal
from pydantic import BaseModel, Field
from etl.core.base_api import BaseAPIClient

class NewSourceParams(BaseModel):
    """Pydantic model with explicit parameter options."""
    param1: Literal["option1", "option2"] = Field(default="option1")
    param2: str = Field(default="default_value")

class NewSourceAPI(BaseAPIClient):
    base_url = "https://api.example.com/data"
    params_model = NewSourceParams

    def get_default_output_filename(self) -> str:
        return "new_source_data.csv"
```

2. Create corresponding ETL pipeline scripts in `etl/pipelines/`:
   - `bronze_new_source.py`
   - `silver_new_source.py`
   - `gold_new_source.py`

3. Update the backend API in `backend/main.py` to serve the new data.

### API Endpoints

The FastAPI backend provides:

- `GET /` - API information
- `GET /health` - Health check and data availability
- `GET /api/emi-retail` - Get paginated electricity data
  - Query params: `limit` (default: 100), `offset` (default: 0)
- `GET /api/emi-retail/summary` - Get summary statistics

### Dashboard Features

Both dashboards provide:

- Connection status to backend API
- Paginated data viewing
- Summary statistics
- Data download as CSV
- Responsive layout

## 🔐 Configuration

Environment variables in `.env`:

```ini
# Data directories
DATA_DIR=./data
BRONZE_DIR=./data/bronze
SILVER_DIR=./data/silver
GOLD_DIR=./data/gold

# API settings
API_TIMEOUT=30
API_RETRY_ATTEMPTS=3

# Backend settings
BACKEND_HOST=localhost
BACKEND_PORT=8000

# Frontend settings
STREAMLIT_PORT=8501
SHINY_PORT=8502
```

## 📦 Dependencies

Core dependencies (defined in `pyproject.toml`):

- **pandas** - Data manipulation
- **pydantic** - Data validation
- **requests** - HTTP client
- **fastapi** - Backend API
- **uvicorn** - ASGI server
- **duckdb** - SQL analytics engine
- **streamlit** - Dashboard framework
- **shiny** - Dashboard framework
- **python-dotenv** - Environment management

Dev dependencies:

- **ruff** - Linting and formatting
- **pytest** - Testing framework
- **pre-commit** - Git hooks

## 🐛 Troubleshooting

### Backend not available

Ensure the FastAPI backend is running:
```bash
python -m backend.main
```

### Data not found

Run the ETL pipeline in sequence:
```bash
python -m etl.pipelines.bronze_emi_retail
python -m etl.pipelines.silver_emi_retail
python -m etl.pipelines.gold_emi_retail
```

### Import errors

Ensure virtual environment is activated and dependencies are synced:

**Windows**
```powershell
.venv\Scripts\Activate.ps1
uv sync
```

**macOS/Linux**
```bash
source .venv/bin/activate
uv sync
```

### Permission errors (Windows)

If you get execution policy errors, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📝 License

[Add your license here]

## 🤝 Contributing

[Add contributing guidelines here]

## 📧 Contact

Good Data Institute - [Add contact information]
