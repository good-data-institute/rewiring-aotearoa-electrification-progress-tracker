# ETL with SQL and Python Guide

This guide shows maintainers how to define ETL transformations using **DuckDB SQL** and **Pandas Python** in the medallion architecture.

## 🎯 Philosophy

This project supports **both SQL and Python** for ETL transformations:

- **Use SQL (DuckDB)** for: Set-based operations, aggregations, joins, filtering
- **Use Python (Pandas)** for: Complex business logic, API calls, iterative processing
- **Mix both**: Start with SQL for data shaping, then use Pandas for final touches

## 📊 Architecture Overview

```
Bronze → Silver → Gold
  ↓        ↓       ↓
 Raw    Clean   Analytics
  ↓        ↓       ↓
Both SQL and Python available at each layer
```

## 🔧 Basic Usage

### Option 1: Pure SQL Approach

```python
from etl.core.medallion import GoldLayer
from pathlib import Path

class SQLProcessor(GoldLayer):
    def process(self, input_path: Path, output_path: Path):
        # Define transformation entirely in SQL
        query = f"""
        SELECT
            region,
            DATE_TRUNC('month', date_col) as month,
            SUM(value) as total,
            AVG(value) as average
        FROM read_csv_auto('{input_path}')
        WHERE date_col >= '2020-01-01'
        GROUP BY region, month
        ORDER BY month DESC
        """

        # Execute and save
        df = self.execute_duckdb_query(query)
        self.write_csv(df, output_path)
```

### Option 2: Pure Python Approach

```python
from etl.core.medallion import GoldLayer
from pathlib import Path

class PandasProcessor(GoldLayer):
    def process(self, input_path: Path, output_path: Path):
        # Read with Pandas
        df = self.read_csv(input_path)

        # Transform with Pandas
        df['date_col'] = pd.to_datetime(df['date_col'])
        df = df[df['date_col'] >= '2020-01-01']

        df['month'] = df['date_col'].dt.to_period('M')
        result = df.groupby(['region', 'month']).agg({
            'value': ['sum', 'mean']
        }).reset_index()

        # Save
        self.write_csv(result, output_path)
```

### Option 3: Hybrid Approach (Recommended)

```python
from etl.core.medallion import GoldLayer
from pathlib import Path
import pandas as pd

class HybridProcessor(GoldLayer):
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
        GROUP BY region, month
        """

        df = self.execute_duckdb_query(query)

        # Use Pandas for business logic
        df['avg_per_record'] = df['total_value'] / df['record_count']
        df['category'] = df['total_value'].apply(
            lambda x: 'High' if x > 1000 else 'Low'
        )
        df['processed_at'] = pd.Timestamp.now()

        self.write_csv(df, output_path)
```

## 📚 Common ETL Patterns

### Pattern 1: Deduplication (Silver Layer)

```python
class DeduplicationProcessor(SilverLayer):
    def process(self, input_path: Path, output_path: Path):
        # SQL approach - keep latest record per ID
        query = f"""
        SELECT DISTINCT ON (id)
            *
        FROM read_csv_auto('{input_path}')
        ORDER BY id, timestamp DESC
        """

        df = self.execute_duckdb_query(query)
        self.write_csv(df, output_path)
```

### Pattern 2: Time Series Aggregation (Gold Layer)

```python
class TimeSeriesProcessor(GoldLayer):
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

        df = self.execute_duckdb_query(query)

        # Calculate day-over-day change
        df['consumption_change'] = df['daily_consumption'] - df['prev_day_consumption']
        df['change_pct'] = (df['consumption_change'] / df['prev_day_consumption'] * 100).round(2)

        self.write_csv(df, output_path)
```

### Pattern 3: Multi-File Join (Gold Layer)

```python
class JoinProcessor(GoldLayer):
    def process(self, input_path: Path, output_path: Path):
        # Assume we have multiple files in silver layer
        silver_dir = input_path.parent

        query = f"""
        SELECT
            c.date,
            c.region,
            c.consumption,
            p.price,
            c.consumption * p.price as cost,
            w.temperature,
            w.weather_type
        FROM read_csv_auto('{silver_dir}/consumption.csv') c
        LEFT JOIN read_csv_auto('{silver_dir}/prices.csv') p
            ON c.date = p.date AND c.region = p.region
        LEFT JOIN read_csv_auto('{silver_dir}/weather.csv') w
            ON c.date = w.date AND c.region = w.region
        WHERE c.date >= '2020-01-01'
        """

        df = self.execute_duckdb_query(query)

        # Add business categories
        df['cost_category'] = pd.cut(
            df['cost'],
            bins=[0, 100, 500, float('inf')],
            labels=['Low', 'Medium', 'High']
        )

        self.write_csv(df, output_path)
```

### Pattern 4: Data Quality Checks (Silver Layer)

```python
class QualityCheckProcessor(SilverLayer):
    def process(self, input_path: Path, output_path: Path):
        # Read data
        df = self.read_csv(input_path)

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
        """

        quality_results = self.execute_duckdb_query(quality_query)
        print("\nData Quality Report:")
        print(quality_results)

        # Pandas cleaning
        df = df.dropna(subset=['key_column'])
        df = df[df['date_column'] <= pd.Timestamp.now()]

        self.write_csv(df, output_path)
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
df = self.execute_duckdb_query(query)
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
df = self.execute_duckdb_query(query)

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
final_df = self.execute_duckdb_query(final_query)
```

## 📖 SQL Examples

See `etl/SQL_EXAMPLES.py` for comprehensive SQL query examples including:
- Basic queries and filtering
- Aggregations and window functions
- Data quality checks
- Time series operations
- Joins and pivots
- Deduplication strategies

## 🚀 Quick Reference

### Execute SQL in ETL

```python
# In any processor class
df = self.execute_duckdb_query("SELECT * FROM read_csv_auto('file.csv')")
```

### Read CSV

```python
# Using Pandas
df = self.read_csv(Path('data/file.csv'))
```

### Write CSV

```python
# Using helper method
self.write_csv(df, Path('data/output.csv'))
```

### DuckDB Special Functions

```sql
-- Read CSV with auto schema detection
read_csv_auto('file.csv')

-- Read multiple files
read_csv_auto('data/*.csv')

-- Date functions
DATE_TRUNC('month', date_col)
CURRENT_DATE
date_col + INTERVAL '7 days'

-- Window functions
LAG(value) OVER (PARTITION BY region ORDER BY date)
SUM(value) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
```

## 🎯 Performance Tips

1. **Filter early**: Use SQL WHERE clauses to reduce data before Pandas
2. **Use SQL for joins**: DuckDB is optimized for joining large datasets
3. **Aggregate in SQL**: GROUP BY is faster in SQL than Pandas
4. **Use Pandas for row-wise ops**: When you need to apply custom functions per row
5. **Temp files are OK**: Don't hesitate to write intermediate results

## 📚 Additional Resources

- **DuckDB Documentation**: https://duckdb.org/docs/
- **Pandas Documentation**: https://pandas.pydata.org/docs/
- **SQL Examples**: `etl/SQL_EXAMPLES.py`
- **Project Examples**: See `etl/pipelines/` for working implementations
