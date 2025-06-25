# Capacity Module Test Suite

This directory contains comprehensive tests for the OFSC Capacity module functionality.

## Test Files Overview

### Mocked Tests (Unit Tests)
- **`test_capacity_mocked.py`**: Unit tests for the capacity module using mocked responses
- **`test_quota_mocked.py`**: Quota-specific tests using real server response data captured in `real_responses.json`

### Integration Tests (Real Server)
- **`test_capacity_integration.py`**: Full integration tests for the capacity module against real OFSC server
- **`test_quota_integration.py`**: Quota-specific integration tests against real OFSC server

### Test Data
- **`real_responses.json`**: Captured real server responses for consistent mocking

## Test Coverage

### Functions Tested
- `getAvailableCapacity()` - Get available capacity for resources
- `getQuota()` - Get quota information with flexible parameters

### Models Tested
- `CapacityRequest` - Request model for capacity queries
- `GetCapacityResponse` - Response model for capacity data
- `GetQuotaRequest` - Request model for quota queries with CsvList conversion
- `GetQuotaResponse` - Response model for quota data
- `QuotaAreaItem` - Individual quota area response model
- `CsvList` - Utility model for comma-separated list handling

### Test Scenarios

#### Input Format Testing
- List inputs: `["FLUSA", "CAUSA"]`
- CSV string inputs: `"FLUSA,CAUSA"`
- CsvList object inputs: `CsvList.from_list(["FLUSA", "CAUSA"])`
- Mixed format inputs in same request

#### Parameter Testing
- Required parameters (dates)
- Optional parameters (areas, categories, boolean flags)
- Boolean to lowercase string conversion
- Empty and None parameter handling

#### Real Data Testing
- Real capacity areas: FLUSA, CAUSA
- Real capacity categories: EST, RES, COM
- Current dates (today/tomorrow)
- Multiple date ranges

#### Response Validation
- Model structure validation
- Field type validation
- Optional field handling
- Extra field allowance

## Running Tests

### Run All Capacity Tests
```bash
uv run pytest tests/capacity/ -v
```

### Run Only Mocked Tests (Fast)
```bash
uv run pytest tests/capacity/test_*_mocked.py -v
```

### Run Only Integration Tests (Requires Credentials)
```bash
uv run pytest tests/capacity/test_*_integration.py -v -m integration
```

### Run Performance Tests (Slow)
```bash
uv run pytest tests/capacity/ -v -m slow
```

## Environment Variables Required for Integration Tests

Integration tests require these environment variables in `.env`:
- `OFSC_CLIENT_ID` - Your OFSC client ID
- `OFSC_CLIENT_SECRET` - Your OFSC client secret  
- `OFSC_COMPANY` - Your OFSC company name
- `OFSC_ROOT` - Your OFSC root (optional)

Integration tests will automatically skip if these are not provided.

## Test Marks

- `@pytest.mark.integration` - Tests that require real server connection
- `@pytest.mark.slow` - Tests that may take longer to execute (performance tests)

## Real Server Response Data

The `real_responses.json` file contains actual server responses for these scenarios:
1. **minimal_dates_only** - Request with only dates parameter
2. **with_areas** - Request with specific areas
3. **with_categories** - Request with areas and categories
4. **with_boolean_flags** - Request with boolean parameters (aggregateResults, etc.)

This data ensures mocked tests accurately reflect real server behavior.

## Test Structure

Each test file follows this pattern:
- **Setup**: Fixtures for OFSC instance, test data, real areas/categories
- **Model Tests**: Validation of Pydantic models with real data
- **API Tests**: Function calls with various parameter combinations
- **Integration Tests**: End-to-end testing with real server
- **Performance Tests**: Load and timing tests for production readiness

## Expected Test Results

- **Mocked tests**: Should always pass (no external dependencies)
- **Integration tests**: Will skip without credentials, pass with valid credentials
- **Performance tests**: Should complete within reasonable time thresholds

## Continuous Integration

For CI/CD pipelines:
1. Always run mocked tests (fast, no external dependencies)
2. Run integration tests only when credentials are available
3. Use performance tests for release validation