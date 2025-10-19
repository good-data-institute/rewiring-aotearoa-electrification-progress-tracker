# Base API Client Refactoring

## Overview

The base API client has been refactored to be truly generic and support multiple data source types beyond just HTTP REST APIs.

## Architecture

### Before Refactoring

The original `BaseAPIClient` was tightly coupled to HTTP REST APIs with:
- URL building logic (`_build_url()`)
- Path parameter extraction (`_get_path_params()`)
- Query parameter extraction (`_get_query_params()`)
- HTTP GET request logic (`fetch_data()`)

This made it impossible to use for non-HTTP data sources like Azure Blob Storage.

### After Refactoring

The API client hierarchy now has two layers:

```
BaseAPIClient (Abstract)
├── HTTPAPIClient (for REST APIs)
│   ├── EMIRetailAPI
│   ├── EECAAPI
│   └── GICAPI
└── EMIGenerationAPI (custom, for Azure Blob Storage)
```

## Classes

### `BaseAPIClient` (etl/core/base_api.py)

**Purpose**: Minimal abstract base class providing only universal functionality

**Responsibilities**:
- Parameter validation via Pydantic models
- Settings management
- Abstract method for default filename generation

**Usage**: All API clients inherit from this, either directly or via `HTTPAPIClient`

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel
from etl.core.config import get_settings

class BaseAPIClient(ABC):
    """Base class for API clients with Pydantic parameter validation."""

    params_model: type[BaseModel] | None = None

    def __init__(self, **params):
        self.settings = get_settings()
        if self.params_model:
            self.params = self.params_model(**params)
        else:
            self.params = None

    @abstractmethod
    def get_default_output_filename(self) -> str:
        pass
```

### `HTTPAPIClient` (etl/core/http_api.py)

**Purpose**: HTTP-specific API client for REST APIs

**Responsibilities**:
- URL building with path and query parameters
- HTTP GET requests with retry logic
- Response handling and file saving

**Attributes**:
- `base_url`: URL template with optional `{placeholders}`
- `path_params`: List of parameter names to use in URL path
- Inherited: `params_model`

**Methods**:
- `_get_path_params()`: Extract path parameters from params model
- `_build_url()`: Build complete URL with path params substituted
- `_get_query_params()`: Extract query parameters (non-path params)
- `fetch_data()`: Make HTTP GET request with retry logic

**Usage**: Inherit from this for HTTP-based APIs

```python
class EMIRetailAPI(HTTPAPIClient):
    base_url = "https://www.emi.ea.govt.nz/Retail/Download/DataReport/CSV/{report_id}"
    params_model = EMIRetailParams
    path_params = ["report_id"]

    def get_default_output_filename(self) -> str:
        return f"emi_retail_{self.params.DateFrom}_{self.params.DateTo}.csv"
```

## Updated API Clients

### EMI Retail API (etl/apis/emi_retail.py)

**Changes**:
- Changed from `BaseAPIClient` → `HTTPAPIClient`
- Imports updated to use `etl.core.http_api`
- No other changes needed (fully compatible)

### EECA API (etl/apis/eeca.py)

**Changes**:
- Changed from `BaseAPIClient` → `HTTPAPIClient`
- Imports updated to use `etl.core.http_api`
- Keeps custom `_get_path_params()` override for URL parameter

### GIC API (etl/apis/gic.py)

**Changes**:
- Changed from `BaseAPIClient` → `HTTPAPIClient`
- Imports updated to use `etl.core.http_api`
- Keeps custom `_get_path_params()` override for URL parameter

### EMI Generation API (etl/apis/emi_generation.py)

**Changes**:
- Inherits directly from `BaseAPIClient` (not HTTPAPIClient)
- Uses Azure Blob Storage SDK instead of HTTP requests
- Custom implementation of data fetching methods:
  - `fetch_generation_data()`: Scans blob storage for CSV files
  - `fetch_concordance()`: HTTP request for concordance data
- Still benefits from parameter validation and settings management

## Benefits

1. **Separation of Concerns**: HTTP-specific logic is isolated in `HTTPAPIClient`
2. **Flexibility**: Non-HTTP data sources can inherit from `BaseAPIClient` directly
3. **Maintainability**: Changes to HTTP logic don't affect non-HTTP clients
4. **Code Reuse**: HTTP clients still share common functionality via `HTTPAPIClient`
5. **Extensibility**: Easy to add new client types (e.g., `S3APIClient`, `DatabaseClient`)

## Migration Guide

### For Existing HTTP APIs

Replace:
```python
from etl.core.base_api import BaseAPIClient

class MyAPI(BaseAPIClient):
    base_url = "https://example.com/api"
    params_model = MyParams
    path_params = ["id"]
```

With:
```python
from etl.core.http_api import HTTPAPIClient

class MyAPI(HTTPAPIClient):
    base_url = "https://example.com/api"
    params_model = MyParams
    path_params = ["id"]
```

### For New Non-HTTP APIs

Inherit directly from `BaseAPIClient`:
```python
from etl.core.base_api import BaseAPIClient

class MyCustomAPI(BaseAPIClient):
    params_model = MyParams

    def fetch_data(self):
        # Custom implementation
        pass

    def get_default_output_filename(self) -> str:
        return "my_data.csv"
```

## Testing

All existing tests should continue to pass without modification. The refactoring maintains backward compatibility for all HTTP-based API clients.

## Future Enhancements

Potential additional client types:
- `S3APIClient`: For AWS S3 data sources
- `FTPAPIClient`: For FTP/SFTP data sources
- `DatabaseAPIClient`: For database connections
- `GraphQLAPIClient`: For GraphQL endpoints
