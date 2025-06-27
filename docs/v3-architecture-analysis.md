# OFSC Python Wrapper v3.0 Architecture Analysis

## Current State Analysis (v2.14.1)

### 1. Project Structure

```
ofsc/
├── __init__.py         # Main OFSC class orchestrator
├── core.py             # Core API functions
├── metadata.py         # Metadata API functions
├── capacity.py         # Capacity API functions
├── oauth.py            # OAuth2 authentication
├── models.py           # Pydantic models
├── common.py           # Shared utilities and decorators
└── exceptions.py       # Custom exceptions
```

### 2. Technology Stack

#### Runtime Dependencies
- **HTTP Client**: `requests` (v2.28.1+)
- **Data Validation**: `pydantic` (v2.6.3+)
- **Caching**: `cachetools` (v5.3.1+)
- **Configuration**: `pydantic-settings` (v2.2.1+)

#### Development Dependencies
- **Testing**: `pytest` (v8.3.3+)
- **Test Data**: `Faker`
- **Environment Management**: `python-dotenv`, `pytest-env`
- **Security**: `pyarmor`, `pyjwt`, `cryptography`

### 3. Current Design Patterns

#### 3.1 API Architecture
- **Modular Design**: Separate classes for different API domains (Core, Metadata, Capacity, OAuth)
- **Base Class Pattern**: `OFSApi` provides common functionality
- **Decorator Pattern**: `@wrap_return` for uniform response handling
- **Method Routing**: Dynamic method routing for backwards compatibility

#### 3.2 Authentication
- **Multi-Auth Support**: Basic Auth (default) and OAuth2
- **Token Caching**: Automatic token refresh with TTL cache
- **Header Management**: Automatic header construction based on auth type

#### 3.3 Response Handling
- **Multiple Response Modes**: OBJ (default), TEXT, FULL, FILE
- **Model Conversion**: Automatic Pydantic model conversion with `auto_model`
- **Error Handling**: Configurable exception raising with `auto_raise`
- **Consistent Wrapping**: All responses wrapped in standardized format

#### 3.4 Data Models
- **Pydantic BaseModel**: All models inherit from BaseModel
- **Type Safety**: Strong typing with Optional and Union types
- **Generic Types**: `OFSResponseList[T]` for paginated responses
- **Field Validation**: Built-in validators and field aliases
- **Special Types**: `CsvList` for comma-separated values

#### 3.5 Configuration
- **Environment-Based**: Uses environment variables
- **Pydantic Settings**: `OFSConfig` model for configuration
- **Auto-Configuration**: Base URL generation from instance name
- **Flexible Initialization**: Multiple ways to configure client

#### 3.6 Testing
- **Framework**: pytest with fixtures
- **Test Types**: Integration, mocked, and model validation tests
- **Test Organization**: Modular structure mirroring API modules
- **Demo Data**: Fixtures for consistent testing

### 4. Code Quality Practices

#### 4.1 Type Hints
- Comprehensive type annotations throughout codebase
- Use of typing module features (Optional, Union, List, Dict)
- Generic types for flexible model handling

#### 4.2 Documentation
- Docstrings on all public methods
- Examples in README and dedicated examples folder
- Response examples for reference

#### 4.3 Error Handling
- Custom exception hierarchy
- Status code mapping
- Informative error messages

#### 4.4 Backwards Compatibility
- Dynamic method routing for legacy API calls
- Deprecation warnings for old usage patterns
- Version management in metadata

## Proposed Improvements for v3.0

### 1. Async Support
- **Migration to httpx**: Replace `requests` with `httpx` for async/await support
- **Async Client**: Create `AsyncOFSC` class using httpx.AsyncClient()
- **Sync Client**: Create `OFSC` class using httpx.Client() (not a wrapper)
- **Connection Pooling**: Leverage httpx's connection pooling

### 2. Enhanced Model Support
- **Response Models**: Every API response should have a corresponding Pydantic model
- **Request Validation**: Internal validation using Pydantic models (not exposed in API)
- **Model Validation**: Stricter validation with custom validators
- **Model Documentation**: Auto-generated documentation from models
- **Raw Response Access**: Models include optional raw_response property

### 3. Architecture Improvements

#### 3.1 Client Design
```python
# Synchronous client
client = OFSC(instance="demo", client_id="id", client_secret="secret")
response = client.core.get_activities()

# Async client
async_client = AsyncOFSC(instance="demo", client_id="id", client_secret="secret")
response = await async_client.core.get_activities()
```

#### 3.2 Response Handling
- **Typed Responses**: All methods return typed Pydantic models
- **Raw Response Property**: Access httpx response via model.raw_response
- **Exception-Only**: All errors raise typed exceptions

#### 3.3 Error Handling
- **Typed Exceptions**: Different exception types for different error categories
- **Retry Logic**: Built-in retry with exponential backoff
- **Circuit Breaker**: Prevent cascading failures
- **Better Error Context**: Include request details in exceptions

### 4. Connection Management
- **Connection Reuse**: httpx's connection pooling
- **Concurrent Requests**: Async support for parallel operations
- **Proper Resource Cleanup**: Context managers for connection lifecycle

### 5. Developer Experience
- **Type Stubs**: Complete type coverage for IDE support
- **Plugin System**: Extensible architecture for custom behaviors
- **Middleware Support**: Request/response interceptors
- **Logging**: Structured logging with configurable levels

### 6. Testing Enhancements
- **Multi-Layer Testing**: Four test types - model validation, mock, live mock, and live tests
- **Async Test Support**: pytest-asyncio with shared fixtures for sync/async
- **Mock Framework**: respx for httpx mocking, custom mock server for integration
- **Test Configuration**: config.test.toml with multi-environment support
- **Test Isolation**: Unique prefixes and concurrent test limits (max 10)
- **Coverage Target**: 80% with HTML reporting
- **Debug Support**: Automatic debug logs on test failure

### 7. Security Improvements
- **Token Rotation**: Automatic token rotation for OAuth2
- **Audit Logging**: Track all API calls for security auditing

### 8. Configuration Enhancements
- **Config Profiles**: Support for multiple configuration profiles
- **Config Validation**: Stricter validation of configuration values
- **Dynamic Config**: Runtime configuration changes
- **Config Sources**: Support for multiple config sources (env, file, code)
- **File-based Credentials**: config.toml for storing credentials

#### config.toml Structure
```toml
[credentials]
instance = "your_instance"
client_id = "your_client_id"
client_secret = "your_client_secret"

[credentials.oauth2]
# Optional OAuth2 settings
token_url = "custom_token_url"
scope = "custom_scope"
```

### 9. Monitoring and Observability
- **Tracing**: OpenTelemetry support for distributed tracing
- **Debug Mode**: Enhanced debug logging for troubleshooting

### 10. Documentation and Examples
- **API Documentation**: Auto-generated from code and models
- **Interactive Examples**: Jupyter notebooks with examples
- **Migration Guide**: Clear path from v2 to v3
- **Best Practices**: Guide for optimal usage patterns

## Migration Strategy

### Phase 1: Foundation (Breaking Changes)
1. Create new async client with httpx
2. Implement all endpoints with Pydantic models
3. Maintain backwards compatibility layer

### Phase 2: Enhancement (Additive Changes)
1. Implement monitoring and observability
2. Enhance error handling and retries

### Phase 3: Polish (Quality Improvements)
1. Complete documentation
2. Add comprehensive examples

## Response Model Design Pattern

All response models follow this pattern to provide both strict typing and raw response access:

```python
from pydantic import BaseModel, ConfigDict
from typing import Optional
import httpx

class BaseOFSResponse(BaseModel):
    """Base class for all OFSC API responses."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    _raw_response: Optional[httpx.Response] = None
    
    @property
    def raw_response(self) -> Optional[httpx.Response]:
        """Access the underlying httpx Response object if available."""
        return self._raw_response
    
    @property
    def status_code(self) -> Optional[int]:
        """Get HTTP status code from raw response."""
        return self._raw_response.status_code if self._raw_response else None
    
    @property
    def headers(self) -> Optional[httpx.Headers]:
        """Get HTTP headers from raw response."""
        return self._raw_response.headers if self._raw_response else None

class ActivityResponse(BaseOFSResponse):
    """Response model for activity data."""
    activity_id: str
    status: str
    activity_type: str
    # ... other fields

# Usage example:
activity = await client.core.get_activity("123")
print(activity.activity_id)  # Typed access
print(activity.raw_response.headers)  # Raw response access
```

## Breaking Changes Summary

1. **Default Response Type**: Models instead of dictionaries
2. **Dual Implementation**: Both sync and async clients using respective httpx clients
3. **Stricter Validation**: All inputs validated through Pydantic
4. **New Exception Hierarchy**: More specific exception types
5. **Configuration Changes**: New configuration model
6. **Python Version**: Minimum Python 3.12 (up from 3.8)
7. **HTTP Client**: httpx instead of requests
8. **Response Access**: Direct attribute access instead of dictionary keys
9. **Error Handling**: Always raises exceptions (no configurable return)
10. **Parameter Naming**: `company`/`companyName` → `instance`

## Backwards Compatibility

- Maintain v2 compatible client as `OFSCV2` 
- OFSCV2 continues to accept `company` or `companyName` parameters
- Deprecation warnings for old patterns
- Migration utilities for easy transition
- Compatibility layer for 1 major version (until v4.0)

### Parameter Name Changes (v2 → v3)
- `company` / `companyName` → `instance`
- Environment variable: `OFSC_COMPANY` → `OFSC_INSTANCE`