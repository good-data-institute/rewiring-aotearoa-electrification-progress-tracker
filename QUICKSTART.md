# Quick Reference Guide

## Quick Commands

### Setup (First Time Only)

```powershell
# Windows
uv venv --python 3.12
.venv\Scripts\Activate.ps1
uv pip install -e ".[dev]"
pre-commit install
```

```bash
# macOS/Linux
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"
pre-commit install
```

### Daily Workflow

#### 1. Run Complete ETL Pipeline

```bash
python run_pipeline.py
```

Or run stages individually:

```bash
python -m etl.pipelines.bronze_emi_retail
python -m etl.pipelines.silver_emi_retail
python -m etl.pipelines.gold_emi_retail
```

#### 2. Start Backend (Terminal 1)

```powershell
# Windows
.venv\Scripts\Activate.ps1
python -m backend.main
```

```bash
# macOS/Linux
source .venv/bin/activate
python -m backend.main
```

#### 3. Start Dashboard (Terminal 2)

**Streamlit:**
```bash
streamlit run frontend/streamlit_app.py
```

**Shiny:**
```bash
shiny run frontend/shiny_app.py --port 8502
```

## Project URLs

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Streamlit Dashboard: http://localhost:8501
- Shiny Dashboard: http://localhost:8502

## Useful Commands

### Code Quality

```bash
# Lint and format
ruff check --fix .
ruff format .

# Run pre-commit on all files
pre-commit run --all-files
```

### Testing

```bash
pytest
```

### Update Dependencies

```bash
uv pip install --upgrade -e ".[dev]"
```

## File Locations

- **Raw data (Bronze)**: `data/bronze/emi_retail/`
- **Cleaned data (Silver)**: `data/silver/emi_retail/`
- **Analytics data (Gold)**: `data/gold/emi_retail/`
- **Configuration**: `.env`
- **Logs**: Check terminal output

## Common Issues

### "Module not found"
```bash
# Ensure virtual environment is activated
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # macOS/Linux

# Reinstall project
uv pip install -e ".[dev]"
```

### "Backend not available"
```bash
# Ensure backend is running in separate terminal
python -m backend.main
```

### "Data not found"
```bash
# Run ETL pipeline first
python run_pipeline.py
```

## Adding New Data Source

1. Create API client: `etl/apis/new_source.py`
2. Create pipelines: `etl/pipelines/{bronze,silver,gold}_new_source.py`
3. Add backend endpoint: `backend/main.py`
4. Update dashboard: `frontend/{streamlit,shiny}_app.py`

See README.md for detailed examples.
