"""
Data Flow Visualization
=======================

This document shows the complete data flow through the system.

┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 1. DATA INGESTION (Bronze Layer)                                        │
└─────────────────────────────────────────────────────────────────────────┘

    External API
    (EMI Retail)
         │
         │ HTTPS GET Request
         │ (with Pydantic-validated params)
         ↓
    ┌─────────────────┐
    │  API Client     │  ← etl/apis/emi_retail.py
    │  (EMIRetailAPI) │  ← Validates: report_id, Capacity, DateFrom, etc.
    └────────┬────────┘
             │
             │ Raw CSV Data
             ↓
    ┌─────────────────┐
    │  Bronze Layer   │  ← data/bronze/emi_retail/*.csv
    │  (Raw Storage)  │  ← etl/pipelines/bronze_emi_retail.py
    └─────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 2. DATA CLEANING (Silver Layer)                                         │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │  Bronze Layer   │
    └────────┬────────┘
             │
             │ Read CSV
             ↓
    ┌─────────────────────────┐
    │  Pandas DataFrame       │
    │  • Remove duplicates    │
    │  • Standardize columns  │
    │  • Handle missing data  │
    └──────────┬──────────────┘
               │
               │ DuckDB Validation
               ↓
    ┌─────────────────────────┐
    │  DuckDB In-Memory       │
    │  • Data quality checks  │
    │  • SQL-based validation │
    └──────────┬──────────────┘
               │
               │ Cleaned CSV
               ↓
    ┌─────────────────┐
    │  Silver Layer   │  ← data/silver/emi_retail/*.csv
    │  (Clean Data)   │  ← etl/pipelines/silver_emi_retail.py
    └─────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 3. DATA TRANSFORMATION (Gold Layer)                                     │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │  Silver Layer   │
    └────────┬────────┘
             │
             │ Read CSV
             ↓
    ┌─────────────────────────┐
    │  Business Logic         │
    │  • Aggregations         │
    │  • Calculated fields    │
    │  • DuckDB SQL queries   │
    │  • Pandas transforms    │
    └──────────┬──────────────┘
               │
               │ Analytics-Ready CSV
               ↓
    ┌─────────────────┐
    │  Gold Layer     │  ← data/gold/emi_retail/*.csv
    │  (Analytics)    │  ← etl/pipelines/gold_emi_retail.py
    └─────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 4. API SERVING (Backend)                                                │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │  Gold Layer     │
    └────────┬────────┘
             │
             │ Read CSV
             ↓
    ┌─────────────────────────┐
    │  FastAPI Backend        │  ← backend/main.py
    │  Endpoints:             │
    │  • GET /                │
    │  • GET /health          │
    │  • GET /api/emi-retail  │
    │  • GET /api/.../summary │
    └──────────┬──────────────┘
               │
               │ JSON Response
               ↓
    ┌─────────────────┐
    │  HTTP Response  │
    │  (JSON)         │
    │  localhost:8000 │
    └─────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 5. VISUALIZATION (Frontend)                                             │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │  FastAPI Backend│
    └────┬───────┬────┘
         │       │
         │       │ HTTP GET
         │       │
    ┌────↓───┐ ┌↓──────────┐
    │Streamlit│ │   Shiny   │
    │Dashboard│ │ Dashboard │
    │:8501    │ │  :8502    │
    └────┬────┘ └┬──────────┘
         │       │
         │       │ Renders
         ↓       ↓
    ┌────────────────────────┐
    │  User's Web Browser    │
    │  • Data tables         │
    │  • Summary stats       │
    │  • CSV downloads       │
    │  • Interactive controls│
    └────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ KEY TECHNOLOGIES AT EACH STAGE                                          │
└─────────────────────────────────────────────────────────────────────────┘

Bronze:
  • requests (HTTP client)
  • Pydantic (parameter validation)
  • CSV (file format)

Silver:
  • Pandas (data cleaning)
  • DuckDB (SQL validation)
  • CSV (file format)

Gold:
  • Pandas (transformations)
  • DuckDB (SQL aggregations)
  • CSV (file format)

Backend:
  • FastAPI (REST API)
  • Uvicorn (ASGI server)
  • Pandas (data reading)

Frontend:
  • Streamlit (dashboard)
  • Shiny (alternative dashboard)
  • requests (HTTP client)

┌─────────────────────────────────────────────────────────────────────────┐
│ CONFIGURATION & QUALITY                                                 │
└─────────────────────────────────────────────────────────────────────────┘

Configuration:
  .env ──→ Pydantic Settings ──→ All Components

Code Quality:
  Git Commit ──→ Pre-commit Hooks ──→ Ruff (lint/format)

Package Management:
  pyproject.toml ──→ UV ──→ Virtual Environment

┌─────────────────────────────────────────────────────────────────────────┐
│ EXECUTION SEQUENCE                                                      │
└─────────────────────────────────────────────────────────────────────────┘

  1. python run_pipeline.py
     ├── Bronze: Fetch from API → data/bronze/
     ├── Silver: Clean data → data/silver/
     └── Gold: Transform data → data/gold/

  2. python -m backend.main
     └── Serve gold data via FastAPI on port 8000

  3. streamlit run frontend/streamlit_app.py  (OR)
     shiny run frontend/shiny_app.py
     └── Display data in web browser

┌─────────────────────────────────────────────────────────────────────────┐
│ EXTENSIBILITY POINTS                                                    │
└─────────────────────────────────────────────────────────────────────────┘

Add New Data Source:
  1. etl/apis/new_source.py (API client + Pydantic model)
  2. etl/pipelines/bronze_new_source.py (ingestion)
  3. etl/pipelines/silver_new_source.py (cleaning)
  4. etl/pipelines/gold_new_source.py (transformation)
  5. backend/main.py (add endpoint)
  6. frontend/*.py (update dashboards)

Customize Processing:
  • Override MedallionLayer.process() methods
  • Add custom DuckDB queries
  • Implement business logic in gold layer
  • Add Pandas transformations

"""
