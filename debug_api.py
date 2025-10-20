"""Debug script to test the API endpoint directly without HTTP."""

import pandas as pd
from backend.repository import DataRepository

# Try to query the data directly
repository = DataRepository()

print("Testing emi_retail metrics query...")
try:
    df = repository.query_metrics(
        dataset="emi_retail", filters=None, limit=100, offset=None
    )
    print(f"✓ Query successful! Got {len(df)} rows")
    print(f"Columns: {list(df.columns)}")
    print("\nFirst few rows:")
    print(df.head())

    print("\nData types:")
    print(df.dtypes)

    print("\nChecking for NaN values:")
    print(df.isna().sum())

    print("\nChecking for datetime columns:")
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            print(f"  {col}: datetime column")

    print("\nTrying to convert to records (OLD WAY - will fail with timestamps)...")
    try:
        records_old = df.replace({pd.NA: ""}).fillna(value="").to_dict(orient="records")
        import json

        json.dumps({"data": records_old[:5]})
        print("✓ Old conversion worked (no timestamps present)")
    except TypeError as e:
        print(f"✗ Old conversion failed: {e}")

    print("\nTrying to convert to records (NEW WAY - with timestamp handling)...")
    df_copy = df.copy()
    for col in df_copy.columns:
        if pd.api.types.is_datetime64_any_dtype(df_copy[col]):
            df_copy[col] = df_copy[col].dt.strftime("%Y-%m-%d %H:%M:%S")
    records = df_copy.replace({pd.NA: ""}).fillna(value="").to_dict(orient="records")
    print(f"✓ Conversion successful! Got {len(records)} records")

    print("\nTrying to convert to JSON...")
    import json

    json_str = json.dumps({"data": records[:5]})  # Just first 5 for testing
    print("✓ JSON serialization successful!")
    print("\nSample record:")
    print(json.dumps(records[0], indent=2))


except Exception as e:
    print("✗ Error occurred:")
    print(f"  Type: {type(e).__name__}")
    print(f"  Message: {str(e)}")
    import traceback

    traceback.print_exc()
