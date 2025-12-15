# ETL Development Guide

A comprehensive guide for building ETL pipelines using **DuckDB SQL** and **Pandas Python**. Includes practical examples for running pipelines, customizing parameters, and troubleshooting common issues.

## 🎯 Philosophy

This project uses both SQL and Python for ETL transformations:

- **Use SQL (DuckDB)** for: Set-based operations, aggregations, joins, filtering
- **Use Python (Pandas)** for: Complex business logic, API calls, iterative processing
- **Mix both**: Start with SQL for data shaping, then use Pandas for final touches



## 🚀 Quick Start

### Basic Structure

```python
from etl.core.pipeline import ProcessedLayer
from pathlib import Path

class MyProcessor(ProcessedLayer):
    def process(self, input_path: Path, output_path: Path):
        # Your transformation logic here
        pass
```

### Execute SQL Query

```python
# In any processor class
df = self.execute_query("SELECT * FROM read_csv_auto('file.csv')")
```

### Read and Write CSV

```python
# Read using Pandas
df = self.read_csv(Path('data/file.csv'))

# Write to CSV
self.write_csv(df, Path('data/output.csv'))
```



## 🔧 ETL Approaches

### Option 1: Pure SQL Approach

**When to use:** Heavy aggregations, joins, filtering on large datasets

```python
from etl.core.pipeline import ProcessedLayer
from pathlib import Path

class SQLProcessor(ProcessedLayer):
    def process(self, input_path: Path, output_path: Path):
        # Define transformation entirely in SQL
        query = f"""
        SELECT
            region,
            DATE_TRUNC('month', date_col) as month,
            SUM(value) as total,
            AVG(value) as average,
            COUNT(*) as record_count
        FROM read_csv_auto('{input_path}')
        WHERE date_col >= '2020-01-01'
        GROUP BY region, DATE_TRUNC('month', date_col)
        ORDER BY month DESC
        """

        # Execute and save
        df = self.execute_query(query)
        self.write_csv(df, output_path)
```

### Option 2: Pure Python Approach

**When to use:** Complex business logic, API calls, custom calculations

```python
from etl.core.pipeline import ProcessedLayer
from pathlib import Path
import pandas as pd

class PandasProcessor(ProcessedLayer):
    def process(self, input_path: Path, output_path: Path):
        # Read with Pandas
        df = self.read_csv(input_path)

        # Transform with Pandas
        df['date_col'] = pd.to_datetime(df['date_col'])
        df = df[df['date_col'] >= '2020-01-01']

        df['month'] = df['date_col'].dt.to_period('M')
        result = df.groupby(['region', 'month']).agg({
            'value': ['sum', 'mean', 'count']
        }).reset_index()

        df['category'] = df['total'].apply(lambda x: 'High' if x > 1000 else 'Low')

        # Save
        self.write_csv(result, output_path)
```

### Option 3: Hybrid Approach (Recommended)

**When to use:** Most real-world scenarios

```python
from etl.core.pipeline import ProcessedLayer
from pathlib import Path
import pandas as pd

class HybridProcessor(ProcessedLayer):
    def process(self, input_path: Path, output_path: Path):
        # Use SQL for heavy lifting
        query = f"""
        SELECT
            region,
            DATE_TRUNC('month', date_col) as month,
            SUM(value) as total_value,
            COUNT(*) as record_count
        FROM read_csv_auto('{input_path}')
        WHERE value IS NOT NULL
        GROUP BY region, DATE_TRUNC('month', date_col)
        """

        df = self.execute_query(query)

        # Use Pandas for business logic
        df['avg_per_record'] = df['total_value'] / df['record_count']
        df['category'] = df['total_value'].apply(
            lambda x: 'High' if x > 1000 else 'Low'
        )
        df['processed_at'] = pd.Timestamp.now()

        self.write_csv(df, output_path)
```



## 📚 Common Patterns

### Pattern 1: Deduplication (Processed Layer)

```python
class DeduplicationProcessor(ProcessedLayer):
    def process(self, input_path: Path, output_path: Path):
        # SQL approach - keep latest record per ID
        query = f"""
        SELECT DISTINCT ON (id)
            *
        FROM read_csv_auto('{input_path}')
        ORDER BY id, timestamp DESC
        """

        df = self.execute_query(query)
        self.write_csv(df, output_path)
```

### Pattern 2: Time Series Aggregation (Metrics Layer)

```python
class TimeSeriesProcessor(MetricsLayer):
    def process(self, input_path: Path, output_path: Path):
        query = f"""
        SELECT
            DATE_TRUNC('day', timestamp) as date,
            region,
            SUM(consumption) as daily_consumption,
            AVG(consumption) as avg_consumption,
            MAX(consumption) as peak_consumption,
            LAG(SUM(consumption)) OVER (
                PARTITION BY region
                ORDER BY DATE_TRUNC('day', timestamp)
            ) as prev_day_consumption
        FROM read_csv_auto('{input_path}')
        GROUP BY date, region
        ORDER BY date DESC, region
        """

        df = self.execute_query(query)

        # Calculate day-over-day change
        df['consumption_change'] = df['daily_consumption'] - df['prev_day_consumption']
        df['change_pct'] = (df['consumption_change'] / df['prev_day_consumption'] * 100).round(2)

        self.write_csv(df, output_path)
```

### Pattern 3: Multi-File Join (Metrics Layer)

```python
class JoinProcessor(MetricsLayer):
    def process(self, input_path: Path, output_path: Path):
        # Assume we have multiple files in Processed layer
        Processed_dir = input_path.parent

        query = f"""
        SELECT
            c.date,
            c.region,
            c.consumption,
            p.price,
            c.consumption * p.price as cost,
            w.temperature,
            w.weather_type
        FROM read_csv_auto('{Processed_dir}/consumption.csv') c
        LEFT JOIN read_csv_auto('{Processed_dir}/prices.csv') p
            ON c.date = p.date AND c.region = p.region
        LEFT JOIN read_csv_auto('{Processed_dir}/weather.csv') w
            ON c.date = w.date AND c.region = w.region
        WHERE c.date >= '2020-01-01'
        """

        df = self.execute_query(query)

        # Add business categories
        df['cost_category'] = pd.cut(
            df['cost'],
            bins=[0, 100, 500, float('inf')],
            labels=['Low', 'Medium', 'High']
        )

        self.write_csv(df, output_path)
```

### Pattern 4: Data Quality Checks (Processed Layer)

```python
class QualityCheckProcessor(ProcessedLayer):
    def process(self, input_path: Path, output_path: Path):
        # SQL-based quality checks
        quality_query = f"""
        SELECT
            'Total Records' as check_name,
            COUNT(*) as check_value
        FROM read_csv_auto('{input_path}')

        UNION ALL

        SELECT
            'Null Values in Key Column',
            COUNT(*)
        FROM read_csv_auto('{input_path}')
        WHERE key_column IS NULL

        UNION ALL

        SELECT
            'Future Dates',
            COUNT(*)
        FROM read_csv_auto('{input_path}')
        WHERE date_column > CURRENT_DATE

        UNION ALL

        SELECT
            'Duplicate Rows',
            COUNT(*) - COUNT(DISTINCT *)
        FROM read_csv_auto('{input_path}')
        """

        quality_results = self.execute_query(quality_query)
        print("\nData Quality Report:")
        print(quality_results)

        # Pandas cleaning
        df = self.read_csv(input_path)
        df = df.dropna(subset=['key_column'])
        df = df[df['date_column'] <= pd.Timestamp.now()]

        self.write_csv(df, output_path)
```



## 🔍 SQL Query Examples

### Read CSV with Auto Schema Detection

```sql
SELECT *
FROM read_csv_auto('data/raw/file.csv')
WHERE date_column >= '2020-01-01'
  AND value > 100
ORDER BY date_column DESC;
```

### Window Functions

```sql
SELECT
    date_column,
    region,
    value,
    SUM(value) OVER (
        PARTITION BY region
        ORDER BY date_column
    ) as running_total,
    AVG(value) OVER (
        PARTITION BY region
        ORDER BY date_column
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as moving_avg_7day,
    RANK() OVER (
        PARTITION BY region
        ORDER BY value DESC
    ) as value_rank
FROM read_csv_auto('data/Processed/file.csv')
ORDER BY region, date_column;
```

### Time Series Analysis with Date Functions

```sql
SELECT
    date_column,
    YEAR(date_column) as year,
    MONTH(date_column) as month,
    DAYOFWEEK(date_column) as day_of_week,
    value,
    LAG(value, 1) OVER (ORDER BY date_column) as prev_day_value,
    value - LAG(value, 1) OVER (ORDER BY date_column) as day_over_day_change,
    (value - LAG(value, 1) OVER (ORDER BY date_column)) /
        LAG(value, 1) OVER (ORDER BY date_column) * 100 as pct_change
FROM read_csv_auto('data/Processed/file.csv')
WHERE date_column >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY date_column;
```

### Export Results to CSV

```sql
COPY (
    SELECT
        region,
        SUM(value) as total_value
    FROM read_csv_auto('data/Processed/file.csv')
    GROUP BY region
) TO 'data/Metrics/aggregated.csv' (HEADER, DELIMITER ',');
```



## 🎓 Best Practices

### When to Use SQL (DuckDB)

✅ **Good for:**
- Filtering large datasets
- Aggregations (SUM, AVG, COUNT, etc.)
- Window functions (LAG, LEAD, ROW_NUMBER)
- Joins across multiple files
- GROUP BY operations
- Set operations (UNION, INTERSECT)

```python
# Good: SQL for aggregation
query = """
SELECT region, SUM(value) as total
FROM read_csv_auto('data.csv')
GROUP BY region
"""
df = self.execute_query(query)
```

### When to Use Python (Pandas)

✅ **Good for:**
- Complex conditional logic
- API calls per row
- Custom calculations
- String manipulation requiring regex
- Date parsing with custom formats
- ML model predictions
- Business rules requiring loops

```python
# Good: Pandas for complex logic
df['category'] = df.apply(
    lambda row: calculate_complex_category(row),
    axis=1
)
```

### Combining Both

✅ **Best practice:**

```python
# 1. Use SQL to reduce data size
query = """
SELECT * FROM read_csv_auto('big_file.csv')
WHERE date >= '2020-01-01'
AND region IN ('Auckland', 'Wellington')
"""
df = self.execute_query(query)

# 2. Use Pandas for business logic
df['custom_metric'] = df.apply(custom_calculation, axis=1)

# 3. Use SQL again for final aggregation if needed
temp_path = output_path.parent / 'temp.csv'
self.write_csv(df, temp_path)

final_query = f"""
SELECT region, AVG(custom_metric) as avg_metric
FROM read_csv_auto('{temp_path}')
GROUP BY region
"""
final_df = self.execute_query(final_query)
```



## 🎯 Performance Tips

1. **Filter early**: Use SQL WHERE clauses to reduce data before Pandas
2. **Use SQL for joins**: DuckDB is optimized for joining large datasets
3. **Aggregate in SQL**: GROUP BY is faster in SQL than Pandas
4. **Use Pandas for row-wise ops**: When you need to apply custom functions per row
5. **Temp files are OK**: Don't hesitate to write intermediate results
6. **Pattern matching**: Use `read_csv_auto('data/*.csv')` to read multiple files efficiently
7. **Column selection**: Only SELECT columns you need to reduce memory usage



## 🔌 DuckDB Features

### File Formats

```sql
-- CSV
read_csv_auto('file.csv')

-- Parquet
read_parquet('file.parquet')

-- JSON
read_json_auto('file.json')
```

### Pattern Matching

```sql
-- All CSV files in directory
read_csv_auto('data/*.csv')

-- Recursive search
read_csv_auto('data/**/*.csv')
```

### Date/Time Functions

```sql
-- Truncate to time unit
DATE_TRUNC('month', date_col)
DATE_TRUNC('day', timestamp_col)

-- Extract components
EXTRACT(YEAR FROM date_col)
EXTRACT(MONTH FROM date_col)

-- Current date/time
CURRENT_DATE
CURRENT_TIMESTAMP

-- Date arithmetic
date_col + INTERVAL '7 days'
date_col - INTERVAL '1 month'
```

### String Functions

```sql
-- Case conversion
UPPER(column), LOWER(column)

-- Trimming
TRIM(column), LTRIM(column), RTRIM(column)

-- Manipulation
SUBSTRING(column, start, length)
REPLACE(column, 'old', 'new')
CONCAT(col1, ' ', col2)

-- Aggregation
STRING_AGG(column, ', ')
```

### Window Functions

```sql
-- Ranking
ROW_NUMBER() OVER (...)
RANK() OVER (...)
DENSE_RANK() OVER (...)

-- Lag/Lead
LAG(column, offset) OVER (...)
LEAD(column, offset) OVER (...)

-- Aggregates
SUM(column) OVER (...)
AVG(column) OVER (...)
COUNT(*) OVER (...)
```

### Statistical Functions

```sql
-- Percentiles
PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY column)
PERCENTILE_DISC(0.95) WITHIN GROUP (ORDER BY column)

-- Dispersion
STDDEV(column)
VARIANCE(column)

-- Correlation
CORR(col1, col2)
COVAR_POP(col1, col2)
```

### Performance Features

- **Columnar storage**: Optimized for analytics
- **Parallel execution**: Automatic query parallelization
- **In-memory processing**: Fast data access
- **Vectorized operations**: Efficient batch processing



## 📖 Additional Resources

- **DuckDB Documentation**: https://duckdb.org/docs/
- **Pandas Documentation**: https://pandas.pydata.org/docs/
- **Project Examples**: See `etl/pipelines/` for working implementations
- **Architecture**: See `docs/ARCHITECTURE.md` for system design



## 🚀 Running Pipelines

### Individual Pipeline Execution

#### EECA Energy Consumption

**Extract & Transform:**
```bash
python -m etl.pipelines.eeca.extract_transform
```
- Input: EECA Excel file (API fetched)
- Output: `data/processed/eeca/eeca_energy_consumption_cleaned.csv`

**Analytics:**
```bash
python -m etl.pipelines.eeca.analytics
```
- Input: Cleaned data
- Output: `data/analytics/eeca/eeca_electricity_percentage.csv`
- Metric: `_13_P1_ElecCons` (Electricity % of total energy)

#### GIC Gas Connections

**Extract & Transform:**
```bash
python -m etl.pipelines.gic.extract_transform
```
- Input: GIC Excel file (API fetched)
- Output: `data/processed/gic/gic_gas_connections_cleaned.csv`

**Analytics:**
```bash
python -m etl.pipelines.gic.analytics
```
- Input: Cleaned data
- Output: `data/analytics/gic/gic_gas_connections_analytics.csv`
- Metric: `_10_P1_Gas` (Monthly new connections by region)

#### EMI Electricity Generation

**Extract & Transform:**
```bash
python -m etl.pipelines.emi_generation.extract_transform
```
- Input: EMI Azure Blob Storage CSVs
- Output: `data/processed/emi_generation/emi_generation_cleaned.csv`
- Note: Downloads multiple CSV files

**Analytics:**
```bash
python -m etl.pipelines.emi_generation.analytics
```
- Input: Cleaned data
- Output: `data/analytics/emi_generation/emi_generation_analytics.csv`
- Metric: `_12_P1_EnergyRenew` (Renewable generation share)

### Customizing Date Ranges

#### EECA - Custom Years
```python
from pathlib import Path
from etl.pipelines.eeca.extract_transform import EECAEnergyConsumptionProcessor

processor = EECAEnergyConsumptionProcessor(
    year_from=2018,
    year_to=2022,
)
processor.process(
    input_path=None,
    output_path=Path("data/processed/eeca/eeca_energy_consumption_cleaned.csv")
)
```

#### GIC - Custom Date Range
```python
from pathlib import Path
from etl.pipelines.gic.extract_transform import GICGasConnectionsProcessor

processor = GICGasConnectionsProcessor(
    year_from=2020,
    year_to=2023,
    month_from=1,
    month_to=6,
)
processor.process(
    input_path=None,
    output_path=Path("data/processed/gic/gic_gas_connections_cleaned.csv")
)
```

#### EMI Generation - Custom Years
```python
from pathlib import Path
from etl.pipelines.emi_generation.extract_transform import EMIGenerationProcessor

processor = EMIGenerationProcessor(
    year_from=2022,
    year_to=2024,
)
processor.process(
    input_path=None,
    output_path=Path("data/processed/emi_generation/emi_generation_cleaned.csv")
)
```

## Changelog
- 14 Dec 2025: removed duplicate, outdated, and unnecessary content
- 19 Oct 2025: first version
