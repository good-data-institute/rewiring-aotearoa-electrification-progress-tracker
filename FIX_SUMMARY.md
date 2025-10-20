# API JSON Serialization Fix Summary

## Problem
The API was returning 500 Internal Server Error when accessing `/api/metrics/emi_retail?limit=100` with the error:
```
TypeError: Object of type Timestamp is not JSON serializable
```

## Root Cause
The pandas DataFrame contained:
1. **Timestamp objects** (datetime columns) that aren't JSON-serializable
2. **NaN values** that also aren't JSON-compliant

## Solution Applied

### 1. Added Helper Function
Created `convert_df_to_json_serializable()` in `backend/main.py`:
- Detects datetime/timestamp columns using `pd.api.types.is_datetime64_any_dtype()`
- Converts datetime columns to strings using `.dt.strftime('%Y-%m-%d %H:%M:%S')`
- Replaces NaN/NA values with empty strings
- Returns JSON-serializable list of records

### 2. Updated Both API Endpoints
- `/api/processed/{dataset}` - uses new conversion function
- `/api/metrics/{dataset}` - uses new conversion function

### 3. Added Comprehensive Logging
- Added `logging` module configuration
- All exception handlers now log full tracebacks with `exc_info=True`
- Makes debugging future issues much easier

## Files Modified
- `backend/main.py` - Added helper function and updated endpoints
- `debug_api.py` - Enhanced to test both old and new conversion methods

## Testing
Run the debug script to verify the fix:
```powershell
python debug_api.py
```

This will show:
- Which columns are datetime types
- Whether old conversion fails (it should with timestamps)
- Whether new conversion succeeds
- Sample JSON output

## How It Works Now
1. DataFrame is queried from CSV
2. Copy is made to avoid modifying original
3. Datetime columns are converted to ISO format strings (`YYYY-MM-DD HH:MM:SS`)
4. NaN values are replaced with empty strings
5. Result is converted to list of dictionaries
6. FastAPI successfully serializes to JSON

## Example Output Format
```json
{
  "data": [
    {
      "Date": "2025-08-01 00:00:00",
      "Region": "Auckland",
      "Value": 123.45,
      "EmptyField": ""
    }
  ],
  "metadata": {
    "total_rows": 1000,
    "returned_rows": 100
  }
}
```

Date/timestamp fields are now strings, and missing values are empty strings (not `null` or `NaN`).
