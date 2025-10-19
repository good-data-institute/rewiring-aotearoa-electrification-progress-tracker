# System Architecture

This document describes the system design, data flow, and technical architecture.

## Data Flow Visualization

```mermaid
flowchart TB
    subgraph "Processed Layer (Data)"
        API["External API<br/>(EMI Retail)"]
        APIClient["API Client<br/>(EMIRetailAPI)<br/><br/>etl/apis/emi_retail.py<br/>Validates: report_id,<br/>Capacity, DateFrom, etc."]
        ExtractTransform["Extract & Transform<br/><br/>etl/pipelines/emi/extract_transform.py<br/>- Fetch from API<br/>- Clean data<br/>- Remove duplicates<br/>- Standardize columns"]
        Processed["Processed Layer<br/>(Clean Data)<br/><br/>data/Processed/emi/*.csv"]

        API -->|"HTTPS GET Request<br/>(Pydantic-validated params)"| APIClient
        APIClient -->|"Raw CSV Data"| ExtractTransform
        ExtractTransform -->|"Pandas + DuckDB<br/>Transformations"| Processed
    end

    subgraph "Metrics Layer (Analytics)"
        Processed2["Processed Layer"]
        Business["Business Logic<br/><br/>etl/pipelines/emi/analytics.py<br/>- Aggregations<br/>- Calculated fields<br/>- DuckDB SQL queries<br/>- Pandas transforms"]
        Metrics["Metrics Layer<br/>(Analytics)<br/><br/>data/Metrics/emi/*.csv"]

        Processed2 -->|"Read CSV"| Business
        Business -->|"Analytics-Ready CSV"| Metrics
    end

    subgraph "API SERVING - Backend"
        Metrics2["Metrics Layer"]
        FastAPI["FastAPI Backend<br/><br/>backend/main.py<br/>Endpoints:<br/>- GET /<br/>- GET /health<br/>- GET /api/emi-retail<br/>"]
        HTTP["HTTP Response<br/>(JSON)<br/><br/>localhost:8000"]

        Metrics2 -->|"Read CSV"| FastAPI
        FastAPI -->|"JSON Response"| HTTP
    end

    subgraph "VISUALIZATION - Frontend"
        Backend["FastAPI Backend"]
        Streamlit["Streamlit<br/>Dashboard<br/>:8501"]
        Shiny["Shiny<br/>Dashboard<br/>:8502"]
        Browser["User's Web Browser<br/>- Data tables<br/>- CSV downloads<br/>- Interactive controls"]

        Backend -->|"HTTP GET"| Streamlit
        Backend -->|"HTTP GET"| Shiny
        Streamlit -->|"Renders"| Browser
        Shiny -->|"Renders"| Browser
    end

    Processed --> Processed2
    Metrics --> Metrics2
    HTTP --> Backend

    classDef ProcessedStyle color:#000000,fill:#c0c0c0,stroke:#808080,stroke-width:2px
    classDef MetricsStyle color:#000000,fill:#ffd700,stroke:#b8860b,stroke-width:2px
    classDef backendStyle color:#000000,fill:#87ceeb,stroke:#4682b4,stroke-width:2px
    classDef frontendStyle color:#000000,fill:#98fb98,stroke:#228b22,stroke-width:2px

    class API,APIClient,ExtractTransform,Processed,Processed2 ProcessedStyle
    class Business,Metrics,Metrics2 MetricsStyle
    class FastAPI,HTTP,Backend backendStyle
    class Streamlit,Shiny,Browser frontendStyle
```

## Key Technologies at Each Stage

**Processed (Extract & Transform):**
- requests (HTTP client)
- Pydantic (parameter validation)
- Pandas (data cleaning)
- DuckDB (SQL transformations)
- CSV (file format)

**Metrics (Analytics):**
- Pandas (transformations)
- DuckDB (SQL aggregations)
- CSV (file format)

**Backend:**
- FastAPI (REST API)
- Uvicorn (ASGI server)
- Pandas (data reading)

**Frontend:**
- Streamlit (dashboard)
- Shiny (alternative dashboard)
- requests (HTTP client)

## Configuration & Quality

```mermaid
flowchart LR
    ENV[".env"] --> DotEnv["python-dotenv"]
    DotEnv --> Components["All Components"]

    Git["Git Commit"] --> PreCommit["Pre-commit Hooks"]
    PreCommit --> Ruff["Ruff (lint/format)"]

    PyProject["pyproject.toml"] --> UV["UV"]
    UV --> VEnv["Virtual Environment"]

    classDef configStyle fill:#e6f3ff,stroke:#4d94ff,stroke-width:2px
    class ENV,DotEnv,Components,Git,PreCommit,Ruff,PyProject,UV,VEnv configStyle
```

## Execution Sequence

```mermaid
flowchart TB
    Start["Run ETL Pipeline"]
    Extract["1. Extract & Transform<br/>python -m etl.pipelines.emi.extract_transform<br/>→ data/Processed/emi/"]
    Analytics["2. Analytics<br/>python -m etl.pipelines.emi.analytics<br/>→ data/Metrics/emi/"]

    Backend["python -m backend.main<br/>Serve Metrics data via FastAPI on port 8000"]

    Frontend["streamlit run frontend/streamlit_app.py<br/>OR<br/>shiny run frontend/shiny_app.py"]
    Display["Display data in web browser"]

    Start --> Extract
    Extract --> Analytics
    Analytics --> Backend
    Backend --> Frontend
    Frontend --> Display

    classDef pipelineStyle fill:#ffe6cc,stroke:#ff9933,stroke-width:2px
    classDef serverStyle fill:#e6ccff,stroke:#9933ff,stroke-width:2px
    class Start,Extract,Analytics pipelineStyle
    class Backend,Frontend,Display serverStyle
```

## Technology Stack by Layer

**Processed (Extract & Transform):**
- HTTP Client: `requests`
- Validation: `Pydantic`
- Data Processing: `Pandas`, `DuckDB`
- Storage: CSV files

**Metrics (Analytics):**
- Data Processing: `Pandas`, `DuckDB`
- Storage: CSV files

**Backend:**
- API Framework: `FastAPI`
- Server: `Uvicorn` (ASGI)
- Data Reading: `Pandas`

**Frontend:**
- Dashboards: `Streamlit`, `Shiny for Python`
- HTTP Client: `requests`

**Configuration & Quality:**
- Settings: `Pydantic Settings`, `python-dotenv`
- Code Quality: `Ruff`, `Pre-commit`
- Package Manager: `uv`

## Configuration Flow

```mermaid
flowchart LR
    ENV[".env"] --> DotEnv["python-dotenv"]
    DotEnv --> Components["All Components"]

    Git["Git Commit"] --> PreCommit["Pre-commit Hooks"]
    PreCommit --> Ruff["Ruff (lint/format)"]

    PyProject["pyproject.toml"] --> UV["UV"]
    UV --> VEnv["Virtual Environment"]

    classDef configStyle fill:#e6f3ff,stroke:#4d94ff,stroke-width:2px
    class ENV,DotEnv,Components,Git,PreCommit,Ruff,PyProject,UV,VEnv configStyle
```

## Extensibility

### Adding New Data Source

1. **API Client**: Create `etl/apis/<source>.py`
   - Inherit from `BaseAPIClient`
   - Define Pydantic parameter model

2. **Pipelines**: Create `etl/pipelines/<source>/`
   - `extract_transform.py` → Processed layer (cleaning)
   - `analytics.py` → Metrics layer (aggregations)

3. **Backend**: Add endpoint in `backend/main.py`
   - Read CSV
   - Serve as JSON

4. **Frontend**: Update dashboards
   - Add visualizations in `frontend/streamlit_app.py`
   - Add visualizations in `frontend/shiny_app.py`

### Customizing Processing

- **Processed Layer**: Override `ProcessedLayer.process()` for extract & transform
- **Metrics Layer**: Override `MetricsLayer.process()` for analytics
- **SQL Queries**: Add custom DuckDB queries for SQL-based transformations
- **Business Logic**: Implement in analytics layer with Pandas
