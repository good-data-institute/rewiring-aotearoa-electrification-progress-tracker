"""
DuckDB SQL Examples for ETL
============================

This file contains example SQL queries that maintainers can use in ETL pipelines.
DuckDB supports standard SQL with additional features for data analysis.

USAGE IN ETL PIPELINES:
-----------------------

from etl.core.medallion import SilverLayer, GoldLayer

class MyProcessor(SilverLayer):
    def process(self, input_path, output_path):
        # Use execute_duckdb_query() to run SQL
        query = "SELECT * FROM read_csv_auto('{input_path}')"
        df = self.execute_duckdb_query(query)
        self.write_csv(df, output_path)

"""

# ==============================================================================
# BASIC QUERIES
# ==============================================================================

EXAMPLE_01_READ_CSV = """
-- Read CSV file with automatic schema detection
SELECT *
FROM read_csv_auto('data/bronze/file.csv')
LIMIT 10;
"""

EXAMPLE_02_FILTER_ROWS = """
-- Filter data by conditions
SELECT *
FROM read_csv_auto('data/bronze/file.csv')
WHERE date_column >= '2020-01-01'
  AND value > 100
ORDER BY date_column DESC;
"""

EXAMPLE_03_SELECT_COLUMNS = """
-- Select specific columns and rename them
SELECT
    date_column as reporting_date,
    region_name as region,
    value as consumption_kwh
FROM read_csv_auto('data/bronze/file.csv');
"""

# ==============================================================================
# AGGREGATIONS
# ==============================================================================

EXAMPLE_04_GROUP_BY = """
-- Aggregate data by groups
SELECT
    region,
    DATE_TRUNC('month', date_column) as month,
    SUM(value) as total_value,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    COUNT(*) as record_count
FROM read_csv_auto('data/silver/file.csv')
GROUP BY region, DATE_TRUNC('month', date_column)
ORDER BY month DESC, region;
"""

EXAMPLE_05_WINDOW_FUNCTIONS = """
-- Use window functions for running totals and rankings
SELECT
    date_column,
    region,
    value,
    SUM(value) OVER (PARTITION BY region ORDER BY date_column) as running_total,
    AVG(value) OVER (PARTITION BY region ORDER BY date_column ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as moving_avg_7day,
    RANK() OVER (PARTITION BY region ORDER BY value DESC) as value_rank
FROM read_csv_auto('data/silver/file.csv')
ORDER BY region, date_column;
"""

# ==============================================================================
# DATA QUALITY CHECKS
# ==============================================================================

EXAMPLE_06_DATA_QUALITY = """
-- Comprehensive data quality check
SELECT
    'Total Rows' as metric,
    COUNT(*) as value
FROM read_csv_auto('data/bronze/file.csv')

UNION ALL

SELECT
    'Unique Rows',
    COUNT(DISTINCT *)
FROM read_csv_auto('data/bronze/file.csv')

UNION ALL

SELECT
    'Null Values',
    SUM(CASE WHEN value IS NULL THEN 1 ELSE 0 END)
FROM read_csv_auto('data/bronze/file.csv')

UNION ALL

SELECT
    'Duplicate Rows',
    COUNT(*) - COUNT(DISTINCT *)
FROM read_csv_auto('data/bronze/file.csv');
"""

EXAMPLE_07_COLUMN_PROFILING = """
-- Profile numeric columns
SELECT
    'column_name' as column_name,
    COUNT(*) as total_count,
    COUNT(column_name) as non_null_count,
    COUNT(*) - COUNT(column_name) as null_count,
    MIN(column_name) as min_value,
    MAX(column_name) as max_value,
    AVG(column_name) as avg_value,
    STDDEV(column_name) as std_dev,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY column_name) as q1,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY column_name) as median,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY column_name) as q3
FROM read_csv_auto('data/silver/file.csv');
"""

# ==============================================================================
# JOINS
# ==============================================================================

EXAMPLE_08_JOIN_TABLES = """
-- Join multiple CSV files
SELECT
    a.date_column,
    a.region,
    a.consumption,
    b.price,
    a.consumption * b.price as total_cost
FROM read_csv_auto('data/silver/consumption.csv') a
LEFT JOIN read_csv_auto('data/silver/prices.csv') b
    ON a.date_column = b.date_column
    AND a.region = b.region;
"""

# ==============================================================================
# TIME SERIES OPERATIONS
# ==============================================================================

EXAMPLE_09_TIME_SERIES = """
-- Time series analysis with date functions
SELECT
    date_column,
    YEAR(date_column) as year,
    MONTH(date_column) as month,
    DAYOFWEEK(date_column) as day_of_week,
    value,
    LAG(value, 1) OVER (ORDER BY date_column) as prev_day_value,
    value - LAG(value, 1) OVER (ORDER BY date_column) as day_over_day_change,
    (value - LAG(value, 1) OVER (ORDER BY date_column)) / LAG(value, 1) OVER (ORDER BY date_column) * 100 as pct_change
FROM read_csv_auto('data/silver/file.csv')
WHERE date_column >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY date_column;
"""

EXAMPLE_10_PIVOT = """
-- Pivot data (convert rows to columns)
PIVOT read_csv_auto('data/silver/file.csv')
ON region
USING SUM(value) as total_value
GROUP BY date_column
ORDER BY date_column;
"""

# ==============================================================================
# DEDUPLICATION
# ==============================================================================

EXAMPLE_11_REMOVE_DUPLICATES = """
-- Remove duplicates, keeping the most recent record
SELECT DISTINCT ON (id_column)
    *
FROM read_csv_auto('data/bronze/file.csv')
ORDER BY id_column, date_column DESC;
"""

# ==============================================================================
# CONDITIONAL LOGIC
# ==============================================================================

EXAMPLE_12_CASE_STATEMENTS = """
-- Add calculated columns with conditional logic
SELECT
    date_column,
    region,
    value,
    CASE
        WHEN value < 100 THEN 'Low'
        WHEN value < 500 THEN 'Medium'
        ELSE 'High'
    END as value_category,
    CASE
        WHEN DAYOFWEEK(date_column) IN (6, 7) THEN 'Weekend'
        ELSE 'Weekday'
    END as day_type
FROM read_csv_auto('data/silver/file.csv');
"""

# ==============================================================================
# EXPORT RESULTS
# ==============================================================================

EXAMPLE_13_EXPORT = """
-- Export query results to CSV
COPY (
    SELECT
        region,
        SUM(value) as total_value
    FROM read_csv_auto('data/silver/file.csv')
    GROUP BY region
) TO 'data/gold/aggregated.csv' (HEADER, DELIMITER ',');
"""

# ==============================================================================
# USAGE IN PYTHON
# ==============================================================================

PYTHON_USAGE_EXAMPLE = """
# Example: Using SQL in your ETL pipeline

from etl.core.medallion import GoldLayer
from pathlib import Path

class ElectricityGoldProcessor(GoldLayer):
    def process(self, input_path: Path, output_path: Path):
        # Define your SQL query
        query = f'''
        SELECT
            DATE_TRUNC('month', date_column) as month,
            region,
            SUM(consumption) as total_consumption_kwh,
            AVG(price) as avg_price_per_kwh,
            SUM(consumption * price) as total_cost
        FROM read_csv_auto('{input_path}')
        WHERE date_column >= '2020-01-01'
        GROUP BY DATE_TRUNC('month', date_column), region
        ORDER BY month DESC, region
        '''

        # Execute SQL and get results as DataFrame
        df = self.execute_duckdb_query(query)

        # Continue with Pandas transformations if needed
        df['cost_per_kwh'] = df['total_cost'] / df['total_consumption_kwh']

        # Write to gold layer
        self.write_csv(df, output_path)
        print(f"Processed {len(df)} aggregated records")

# Use in your pipeline script:
# processor = ElectricityGoldProcessor()
# processor.process(
#     input_path=Path('data/silver/electricity.csv'),
#     output_path=Path('data/gold/monthly_summary.csv')
# )
"""

# ==============================================================================
# DUCKDB FEATURES
# ==============================================================================

DUCKDB_FEATURES = """
DuckDB Features Available in ETL:
----------------------------------

1. Read Multiple File Formats:
   - CSV: read_csv_auto('file.csv')
   - Parquet: read_parquet('file.parquet')
   - JSON: read_json_auto('file.json')

2. Pattern Matching:
   - read_csv_auto('data/*.csv')  -- All CSV files
   - read_csv_auto('data/**/*.csv')  -- Recursive

3. Date/Time Functions:
   - DATE_TRUNC('month', date_col)
   - EXTRACT(YEAR FROM date_col)
   - CURRENT_DATE, CURRENT_TIMESTAMP
   - date_col + INTERVAL '7 days'

4. String Functions:
   - UPPER(), LOWER(), TRIM()
   - SUBSTRING(), REPLACE()
   - CONCAT(), STRING_AGG()

5. Array/List Functions:
   - LIST_AGG(), UNNEST()
   - ARRAY operations

6. Window Functions:
   - ROW_NUMBER(), RANK(), DENSE_RANK()
   - LAG(), LEAD()
   - SUM() OVER, AVG() OVER

7. Statistical Functions:
   - PERCENTILE_CONT(), PERCENTILE_DISC()
   - STDDEV(), VARIANCE()
   - CORR(), COVAR_POP()

8. Performance:
   - Columnar storage
   - Parallel query execution
   - In-memory processing
   - Optimized for analytics

For more information: https://duckdb.org/docs/
"""
