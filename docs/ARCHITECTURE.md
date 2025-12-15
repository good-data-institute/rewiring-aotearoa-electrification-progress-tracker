# System Architecture

This document describes the system design, data flow, and technical architecture for the Rewiring Aotearoa Electrification Progress Tracker.

## High-Level System Overview

```mermaid
flowchart LR
    %% External Data Sources
    ExtAPIs[("External APIs<br/>(EMI, EECA, GIC<br/>Waka Kotahi)")]

    %% ETL Pipeline Layer
    subgraph ETL["ETL Pipeline (/etl)"]
        direction TB
        APIs["API Clients<br/>/etl/apis"]
        Core["Core Logic<br/>/etl/core"]
        Pipelines["Pipeline Scripts<br/>/etl/pipelines"]

        APIs --> Core
        Core --> Pipelines
    end

    %% Data Storage Layer
    subgraph Storage["Data Storage (/data)"]
        direction TB
        Raw[("Raw Data<br/>/data/raw")]
        Processed[("Processed Data<br/>/data/processed")]
        Metrics[("Metrics Data<br/>/data/metrics")]

        Raw --> Processed
        Processed --> Metrics
    end

    %% Backend Layer
    subgraph Backend["Backend API (/backend)"]
        direction TB
        Repository["Repository<br/>DuckDB Queries"]
        API["FastAPI<br/>REST Endpoints"]

        Repository --> API
    end

    %% Frontend Layer
    subgraph Frontend["Frontend Apps (/frontend)"]
        direction TB
        Streamlit["Streamlit App<br/>Introduction.py"]
        Shiny["Shiny App<br/>shiny_app.py"]

        Streamlit ~~~ Shiny
    end

    %% User
    User([User])

    %% Main Flow
    ExtAPIs -->|"Extract"| ETL
    ETL -->|"Load"| Storage
    Storage -->|"Query"| Backend
    Backend -->|"HTTP/JSON"| Frontend
    Frontend -->|"View"| User

    %% Styling
    classDef external color:#000000,fill:#e1f5ff,stroke:#0288d1,stroke-width:2px
    classDef etl color:#000000,fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef storage color:#000000,fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef backend color:#000000,fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef frontend color:#000000,fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef user color:#000000,fill:#fff9c4,stroke:#f57f17,stroke-width:3px

    class ExtAPIs external
    class ETL,APIs,Core,Pipelines etl
    class Storage,Raw,Processed,Metrics storage
    class Backend,Repository,API backend
    class Frontend,Streamlit,Shiny frontend
    class User user
```

## Detailed Data Flow Visualization

```mermaid
flowchart TB
    subgraph "Raw Layer (Extraction)"
        API["External API<br/>(EMI, EECA, GIC<br/>Waka Kotahi)"]
        APIClient["API Client<br/>(Pydantic-validated)"]
        Extract["Extract Script<br/><br/>etl/pipelines/*/extract.py<br/>- Fetch from API<br/>- Save raw data<br/>- No transformation"]
        Raw["Raw Layer<br/>(Original Data)<br/><br/>data/raw/*/*.csv/xlsx"]

        API -->|"HTTPS GET Request"| APIClient
        APIClient -->|"Raw Data"| Extract
        Extract -->|"Save as-is"| Raw
    end

    subgraph "Processed Layer (Transformation)"
        Raw2["Raw Layer"]
        Transform["Transform Script<br/><br/>etl/pipelines/*/transform.py<br/>- Read raw data<br/>- Clean & validate<br/>- Standardize columns<br/>- Remove duplicates"]
        Processed["Processed Layer<br/>(Clean Data)<br/><br/>data/processed/*/*.csv"]

        Raw2 -->|"Read Raw"| Transform
        Transform -->|"Pandas + DuckDB"| Processed
    end

    subgraph "Metrics Layer (Analytics)"
        Processed2["Processed Layer"]
        Analytics["Analytics Script<br/><br/>etl/pipelines/*/analytics.py<br/>- Aggregations<br/>- Business metrics<br/>- DuckDB SQL queries<br/>- Pandas transforms"]
        Metrics["Metrics Layer<br/>(Analytics)<br/><br/>data/metrics/*/*.csv"]

        Processed2 -->|"Read Processed"| Analytics
        Analytics -->|"Business-Ready"| Metrics
    end

    subgraph "Backend (API Layer)"
        DataLayers["Data Layers<br/>(Processed + Metrics)"]
        Repository["DuckDB Repository<br/><br/>backend/repository.py<br/>- Query with filters<br/>- Date range support<br/>- Pagination"]
        FastAPI["FastAPI Backend<br/><br/>backend/main.py<br/>Endpoints:<br/>- /api/datasets<br/>- /api/processed/{dataset}<br/>- /api/metrics/{dataset}"]
        HTTP["HTTP Response<br/>(JSON)<br/><br/>localhost:8000"]

        DataLayers -->|"DuckDB Queries"| Repository
        Repository -->|"DataFrame"| FastAPI
        FastAPI -->|"JSON Response"| HTTP
    end

    subgraph "Frontend (Dashboards)"
        Backend["Backend API"]
        Streamlit["Streamlit<br/>Dashboard<br/>:8501<br/>- All datasets<br/>- Simple tables"]
        Shiny["Shiny<br/>Dashboard<br/>:8502<br/>- All datasets<br/>- Simple tables"]
        Browser["User's Browser"]

        Backend -->|"HTTP GET /api/metrics/*"| Streamlit
        Backend -->|"HTTP GET /api/metrics/*"| Shiny
        Streamlit -->|"Renders"| Browser
        Shiny -->|"Renders"| Browser
    end

    Raw --> Raw2
    Processed --> Processed2
    Metrics --> DataLayers
    Processed --> DataLayers
    HTTP --> Backend

    classDef RawStyle color:#000000,fill:#ffcccc,stroke:#cc0000,stroke-width:2px
    classDef ProcessedStyle color:#000000,fill:#c0c0c0,stroke:#808080,stroke-width:2px
    classDef MetricsStyle color:#000000,fill:#ffd700,stroke:#b8860b,stroke-width:2px
    classDef backendStyle color:#000000,fill:#87ceeb,stroke:#4682b4,stroke-width:2px
    classDef frontendStyle color:#000000,fill:#98fb98,stroke:#228b22,stroke-width:2px

    class API,APIClient,Extract,Raw,Raw2 RawStyle
    class Transform,Processed,Processed2 ProcessedStyle
    class Analytics,Metrics,DataLayers MetricsStyle
    class Repository,FastAPI,HTTP,Backend backendStyle
    class Streamlit,Shiny,Browser frontendStyle
```

## Key Technologies

**Raw Layer (Extraction):**
- requests (HTTP client)
- Pydantic (parameter validation)
- CSV/Excel (file formats)
- No transformation logic

**Processed Layer (Transformation):**
- Pandas (data cleaning)
- DuckDB (SQL transformations)
- CSV (file format)

**Metrics Layer (Analytics):**
- Pandas (transformations)
- DuckDB (SQL aggregations)
- CSV (file format)

**Backend (API):**
- FastAPI (REST API)
- DuckDB (query engine)
- Repository pattern (data access)
- Uvicorn (ASGI server)

**Frontend (Dashboards):**
- Streamlit (interactive dashboard)
- Shiny for Python (alternative dashboard)
- requests (HTTP client)
- API-first architecture

## Configuration & Quality

```mermaid
flowchart LR
    ENV[".env"] --> DotEnv["python-dotenv"]
    DotEnv --> Components["All Components"]

    Git["Git Commit"] --> PreCommit["Pre-commit Hooks"]
    PreCommit --> Ruff["Ruff (lint/format)"]

    PyProject["pyproject.toml"] --> UV["UV"]
    UV --> VEnv["Virtual Environment"]

    classDef configStyle color:#000000,fill:#e6f3ff,stroke:#4d94ff,stroke-width:2px
    class ENV,DotEnv,Components,Git,PreCommit,Ruff,PyProject,UV,VEnv configStyle
```

## Execution Sequence

```mermaid
flowchart TB
    Start["Run ETL Pipeline"]

    Extract["1. Extract (API → Raw)<br/>python -m etl.pipelines.*/extract<br/>→ data/raw/*/"]

    Transform["2. Transform (Raw → Processed)<br/>python -m etl.pipelines.*/transform<br/>→ data/processed/*/"]

    Analytics["3. Analytics (Processed → Metrics)<br/>python -m etl.pipelines.*/analytics<br/>→ data/metrics/*/"]

    Backend["4. Start Backend<br/>python -m backend.main<br/>DuckDB repository queries data<br/>FastAPI serves on port 8000"]

    Frontend["5. Start Frontend<br/>streamlit run frontend/Introduction.py<br/>OR<br/>shiny run frontend/shiny_app.py"]

    Display["6. View in Browser<br/>Dashboards fetch from API<br/>Display all metrics datasets"]

    Start --> Extract
    Extract --> Transform
    Transform --> Analytics
    Analytics --> Backend
    Backend --> Frontend
    Frontend --> Display

    classDef rawStyle color:#000000,fill:#ffcccc,stroke:#cc0000,stroke-width:2px
    classDef processedStyle color:#000000,fill:#cccccc,stroke:#666666,stroke-width:2px
    classDef metricsStyle color:#000000,fill:#ffffcc,stroke:#cccc00,stroke-width:2px
    classDef serverStyle color:#000000,fill:#e6ccff,stroke:#9933ff,stroke-width:2px

    class Start,Extract rawStyle
    class Transform processedStyle
    class Analytics metricsStyle
    class Backend,Frontend,Display serverStyle
```

## Extensibility

### Adding New Data Source

1. **API Client**: Create `etl/apis/<source>.py`
   - Inherit from `BaseAPIClient`
   - Define Pydantic parameter model

2. **Pipelines**: Create `etl/pipelines/<source>/`
   - `extract.py` → Raw layer (API to raw storage)
   - `transform.py` → Processed layer (cleaning & transformation)
   - `analytics.py` → Metrics layer (aggregations & business logic)

3. **Backend**: Update `backend/repository.py`
   - Add file mapping in `file_mapping` dictionaries
   - DuckDB will automatically query the new CSV files

4. **Frontend**: No changes needed!
   - Dashboards automatically discover and display all datasets via `/api/datasets` endpoint

### Customizing Processing

- **Raw Layer**: Implement extractor class with `extract()` method to save raw data
- **Processed Layer**: Override `ProcessedLayer.process()` for transform logic
- **Metrics Layer**: Override `MetricsLayer.process()` for analytics
- **Backend Queries**: Add custom filters in repository pattern
- **SQL Queries**: Add custom DuckDB queries for SQL-based transformations
- **Business Logic**: Implement in analytics layer with Pandas or DuckDB SQL

### API Filtering Examples

```bash
# Get metrics with date filter
curl "http://localhost:8000/api/metrics/demo_emi_retail?filter_json={\"Year\":{\"gte\":2020,\"lte\":2025}}"

# Get processed data with pagination
curl "http://localhost:8000/api/processed/eeca?limit=50&offset=100"

# List all available datasets
curl "http://localhost:8000/api/datasets?layer=metrics"
```
