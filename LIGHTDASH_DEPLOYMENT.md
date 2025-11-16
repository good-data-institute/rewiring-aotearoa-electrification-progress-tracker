# Lightdash Metrics Viewer

Lightweight data exploration interface for electrification metrics using Lightdash + DuckDB.

## Files

- **Dockerfile** - Container image with Lightdash CLI and DuckDB
- **lightdash.yaml** - Lightdash configuration (DuckDB + S3)
- **metadata.yaml** - Table definitions for 8 metrics from S3
- **render.yaml** - Render.com deployment configuration

## Data Source

Reads parquet files from public S3: s3://test-gdi-28924/data/metrics/

## Metrics Available

1. Gas Connections (GIC)
2. Renewable Generation (EMI)
3. Electricity Percentage (EECA)
4. Energy by Fuel (EECA)
5. Battery Penetration - Commercial
6. Battery Penetration - Residential
7. Solar Capacity
8. Battery Capacity

## Deploy to Render

1. Push to GitHub
2. Connect repository in Render
3. Render will use render.yaml for configuration
4. Service will auto-deploy on push (if enabled)

## Notes

- Free tier on Render
- No authentication (read-only public data)
- DuckDB queries S3 directly via httpfs
