# OFSC Python Wrapper v3.0 Tests

This directory contains the comprehensive test suite for OFSC Python Wrapper v3.0, following the documented multi-layered testing strategy.

## Test Structure

The test suite implements four distinct test types as outlined in the testing strategy:

### 1. Model Validation Tests (`tests/models/`)
Tests that validate Pydantic models against stored API responses to ensure model correctness.

- `test_core_models.py` - Core API model validation (resources, users)
- `test_metadata_models.py` - Metadata API model validation (properties, work zones, activity types)  
- `test_capacity_models.py` - Capacity API model validation (areas, categories, availability)

**Purpose**: Validate that all Pydantic models correctly parse real API responses
**Data Source**: JSON files in `response_examples/` directory

### 2. Unit Tests (`tests/unit/`)
Unit tests using mocked HTTP responses for isolated testing.

- `test_auth.py` - Authentication system tests (Basic Auth, OAuth2, environment variables)

**Purpose**: Test client logic without external dependencies
**Tool**: `respx` for httpx mocking

### 3. Integration Tests (`tests/integration/`)
Integration tests against a custom mock server that simulates OFSC API.

**Purpose**: Test full request/response cycle with realistic API behavior
*Note: Mock server implementation pending - Phase 2*

### 4. Live Tests (`tests/live/`)
End-to-end tests against real OFSC test environments.

- `test_auth_live.py` - Live authentication tests using OFSC client classes (Basic Auth, OAuth2, token caching, client creation)

**Purpose**: Validate actual API integration
**Marker**: `@pytest.mark.live`

## Configuration

### Test Configuration (`config.test.toml`)
Test-specific configuration separate from main application config:

```toml
[test]
coverage_target = 80
debug_on_failure = true

[test.environments.dev]
url = "https://sunrise0511.fs.ocs.oraclecloud.com"
instance = "sunrise0511"
client_id = "demoauth"
client_secret = "..."
```

### Environment Variables
Configuration precedence (highest to lowest):
1. Environment variables (`OFSC_INSTANCE`, `OFSC_CLIENT_ID`, `OFSC_CLIENT_SECRET`)
2. `.env` file
3. `config.test.toml` file
4. Default values

## Running Tests

### By Test Type
```bash
# Model validation tests
uv run pytest tests/models/ -v

# Unit tests only
uv run pytest tests/unit/ -v

# Integration tests (when implemented)
uv run pytest tests/integration/ -m integration -v

# Live tests
source .env && uv run pytest tests/live/ -m live -v
```

### By Marker
```bash
# Unit tests only
uv run pytest tests/ -m unit -v

# Integration tests only  
source .env && uv run pytest tests/ -m integration -v

# All tests except live
uv run pytest tests/ -m "not live" -v
```

### Environment Selection
```bash
# Run tests for specific environment
uv run pytest tests/ --env dev -v

# Run with live credentials
source .env && uv run pytest tests/ --live -v
```

### Coverage Reports
```bash
# Generate HTML coverage report
uv run pytest tests/ --cov=ofsc --cov-report=html -v

# Terminal coverage report
uv run pytest tests/ --cov=ofsc --cov-report=term-missing -v
```

## Test Data

### Response Examples
Model validation tests use real API responses from `response_examples/`:
- `163_get_resources.json` - Resource list response
- `219_get_users.json` - User list response  
- `50_get_properties.json` - Properties metadata
- `78_get_work_zones.json` - Work zones metadata
- And many more...

### Test Data Directory
`tests/data/` contains test-specific data files and fixtures.

## Current Test Coverage

### ✅ Authentication (28 tests)
- **Location**: `tests/unit/test_auth.py` (17 tests), `tests/live/test_auth_live.py` (11 tests)
- **Coverage**: Basic Auth, OAuth2, environment variables, client integration, live token validation, client creation
- **Status**: Complete

### ✅ Model Validation (12+ tests)
- **Location**: `tests/models/`
- **Coverage**: Core, Metadata, and Capacity API response validation
- **Status**: Basic implementation complete

### 🔄 Planned Test Areas
- API endpoint testing (respx mocking)
- Live integration tests
- Mock server implementation
- Error handling and retry logic
- Connection pooling and timeouts
- Response processing
- Async/sync client feature parity

## Test Configuration Features

### Multi-Environment Support
- Dev, Staging, Production environments
- Environment-specific credentials
- Command-line environment selection

### Debug Mode
- Automatic debug log generation on failures
- Test context preservation
- Request/response logging

### Async Test Handling
- Proper event loop management
- Parametrized sync/async client testing
- Async fixture support

## Legacy Tests

The v2 test suite has been moved to `test_v2/` for reference but is not actively maintained for v3.0 development.

## Testing Strategy Compliance

This test structure follows the documented testing strategy in `docs/v3-testing-strategy.md`:

- ✅ **4 Test Types**: Model validation, Unit, Integration, Live
- ✅ **Configuration Management**: Separate test config with precedence
- ✅ **Fixture Organization**: Shared fixtures in conftest.py
- ✅ **Marker System**: Proper test categorization
- ✅ **Debug Support**: Failure debugging and context preservation
- ✅ **Coverage Targets**: 80% coverage goal
- 🔄 **Mock Server**: Planned for Phase 2
- ✅ **Live Tests**: OAuth2 authentication tests implemented