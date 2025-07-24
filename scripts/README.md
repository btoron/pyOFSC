# pyOFSC Scripts

This directory contains utility scripts for development, testing, and API exploration with the pyOFSC library.

## Overview

The scripts in this directory help with various development tasks including:
- API endpoint data collection and response analysis
- Test performance measurement and optimization
- Swagger specification parsing and endpoint registry generation
- Parallel test execution

## Scripts

### 📊 Data Collection Scripts

#### `collect_endpoint_response.py`
Collects real API responses from OFSC endpoints for testing and development.

**Purpose:** Makes actual API calls to collect response examples for specific endpoints by ID (from ENDPOINTS.md).

**Usage:**
```bash
# Collect response for a simple endpoint
python scripts/collect_endpoint_response.py 27

# Collect response with path parameters
python scripts/collect_endpoint_response.py 28 --label "mobile_provider_request#8#"

# Get property enumeration values
python scripts/collect_endpoint_response.py 54 --label "country_code"

# Multi-parameter endpoints
python scripts/collect_endpoint_response.py 11 --params "demoauth" "metadataAPI"

# Export with specific media type
python scripts/collect_endpoint_response.py 59 --params demoauth Optimization --media-type application/json
```

**Requirements:** Valid OFSC credentials in `.env` file

#### `collect_multiple_responses.py`
Batch collection of API responses for multiple endpoints.

**Purpose:** Efficiently collects response examples from multiple OFSC endpoints using existing credentials.

**Usage:**
```bash
python scripts/collect_multiple_responses.py
```

**Features:**
- Uses authenticated OFSC client
- Collects responses for predetermined endpoint list
- Saves responses with timestamped filenames
- Handles errors gracefully and continues collection

**Requirements:** Valid OFSC credentials in `.env` file

### 🔧 Development Tools

#### `extract_endpoints.py`
Parses swagger.json to generate a comprehensive endpoints registry.

**Purpose:** Creates a structured Python module containing all OFSC API endpoints with their metadata, parameters, and schemas.

**Usage:**
```bash
python scripts/extract_endpoints.py
```

**Output:** Generates `tests/fixtures/endpoints_registry.py` with:
- Complete endpoint information (242 endpoints)
- HTTP methods, paths, and parameters
- Request/response schema references
- Module organization (metadata, core, capacity, etc.)
- Utility functions for endpoint lookups

**Features:**
- Maps endpoint IDs from ENDPOINTS.md documentation
- Extracts parameter constraints (min/max length, types, etc.)
- Organizes endpoints by module and HTTP method
- Provides lookup utilities and statistics
- Generates importable Python dataclasses

**Generated Module Usage:**
```python
from tests.fixtures.endpoints_registry import *

# Get endpoint by ID
endpoint = get_endpoint_by_id(1)
print(f"{endpoint.method} {endpoint.path}")

# Find endpoint by method and path
endpoint = find_endpoint('GET', '/rest/ofscMetadata/v1/properties')

# Get all endpoints for a module
metadata_endpoints = get_endpoints_by_module('metadata')

# Statistics
print(f"Total endpoints: {TOTAL_ENDPOINTS}")
print(f"By module: {ENDPOINTS_COUNT_BY_MODULE}")
```

#### `generate_tests.py`
Generates comprehensive test files for OFSC API endpoints using the swagger specification and endpoint registry.

**Purpose:** Automatically creates complete test files with CRUD operations, parameter validation, negative tests, search/filter tests, and pagination tests.

**Usage:**
```bash
# Generate tests for a specific resource
python scripts/generate_tests.py properties

# Generate tests with custom output path
python scripts/generate_tests.py activities --output tests/custom/my_tests.py

# List all available resources
python scripts/generate_tests.py --list

# Dry run to preview what would be generated
python scripts/generate_tests.py users --dry-run

# Verbose output for detailed information
python scripts/generate_tests.py properties --verbose
```

**Features:**
- **Complete CRUD Testing**: Create, Read, Update, Delete operations
- **Parameter Boundary Testing**: Min/max length, numeric boundaries, enum validation
- **Negative Test Cases**: Not found, invalid parameters, malformed requests
- **Search & Filter Testing**: Query functionality and filter combinations
- **Pagination Testing**: Page traversal, boundary conditions, performance
- **Performance Testing**: Response times, bulk operations, concurrent access
- **Automatic Cleanup**: Generated tests inherit from BaseOFSCTest for resource management

**Generated Test Structure:**
```python
class TestPropertiesAPI(BaseOFSCTest):
    """Comprehensive tests for Properties API endpoints."""
    
    # CRUD Operations
    async def test_create_properties(self):
    async def test_get_properties_by_id(self):
    async def test_list_properties(self):
    async def test_update_properties(self):
    async def test_delete_properties(self):
    
    # Parameter Boundary Tests
    async def test_get_label_boundary_length(self):
    async def test_get_limit_boundary_numeric(self):
    
    # Negative Test Cases  
    async def test_get_properties_not_found(self):
    async def test_get_properties_invalid_params(self):
    
    # Search & Filter Tests
    async def test_get_properties_search(self):
    async def test_get_properties_filter(self):
    
    # Pagination Tests
    async def test_get_properties_pagination(self):
    
    # Performance Tests
    async def test_get_properties_bulk_performance(self):
    async def test_get_properties_concurrent(self):
```

**Integration with BaseOFSCTest:**
- Automatic resource cleanup tracking
- Built-in performance monitoring
- Rate limiting for API compliance
- Detailed error reporting and context
- Unique test resource naming

### ⚡ Performance & Testing Scripts

#### `measure_test_performance.py`
Measures baseline performance of different test categories.

**Purpose:** Benchmarks test execution times to evaluate the impact of parallel execution improvements.

**Usage:**
```bash
python scripts/measure_test_performance.py
```

**Features:**
- Measures execution time for different test categories
- Generates detailed performance reports
- Helps identify optimization opportunities
- Compares sequential vs parallel execution benefits

#### `run_tests_parallel.py`
Intelligent parallel test execution with category-specific controls.

**Purpose:** Optimizes test execution through smart parallelism that respects rate limits and test characteristics.

**Usage:**
```bash
python scripts/run_tests_parallel.py [options]
```

**Features:**
- Category-specific parallelism controls
- Rate limit awareness for live API tests
- CPU core optimization
- Intelligent worker allocation based on test type
- CI/CD environment detection and adaptation

## Script Categories

### 🌐 API Integration Scripts
- `collect_endpoint_response.py` - Single endpoint response collection
- `collect_multiple_responses.py` - Batch response collection

### 🏗️ Development Tools
- `extract_endpoints.py` - Swagger parsing and registry generation

### ⚙️ Testing & Performance
- `measure_test_performance.py` - Performance benchmarking
- `run_tests_parallel.py` - Optimized parallel test execution

## Requirements

### Environment Setup
1. **Python Environment:** Use `uv` for dependency management
   ```bash
   uv run python scripts/<script_name>.py
   ```

2. **OFSC Credentials:** For API collection scripts, create `.env` file:
   ```env
   OFSC_INSTANCE=your_instance
   OFSC_CLIENT_ID=your_client_id
   OFSC_CLIENT_SECRET=your_client_secret
   ```

3. **Project Structure:** Scripts expect standard pyOFSC project structure:
   ```
   pyOFSC/
   ├── scripts/          # This directory
   ├── ofsc/            # Main library code
   ├── tests/           # Test suite
   ├── response_examples/ # API response examples
   └── docs/            # Documentation
   ```

### Dependencies
- **Core:** Python 3.12+, httpx, pydantic
- **API Scripts:** python-dotenv, asyncio
- **Testing Scripts:** pytest, subprocess
- **Development:** json, pathlib, typing

## Usage Patterns

### Development Workflow
1. **API Exploration:** Use `collect_endpoint_response.py` to gather real API responses
2. **Registry Generation:** Run `extract_endpoints.py` after swagger.json updates
3. **Test Optimization:** Use `measure_test_performance.py` to benchmark changes
4. **CI/CD:** Use `run_tests_parallel.py` for optimized test execution

### Testing Workflow
1. Generate endpoint registry with `extract_endpoints.py`
2. Collect real responses with collection scripts
3. Measure baseline performance with `measure_test_performance.py`
4. Run optimized tests with `run_tests_parallel.py`

## Error Handling

All scripts include comprehensive error handling:
- **API Scripts:** Handle authentication failures, rate limits, network errors
- **Development Scripts:** Validate file paths, handle parsing errors
- **Test Scripts:** Graceful degradation, detailed error reporting

## Output Files

### Generated Files
- `tests/fixtures/endpoints_registry.py` - Complete endpoint registry
- `response_examples/*.json` - API response examples
- Performance measurement logs and reports

### Log Files
- Test execution logs with timestamps
- Performance metrics and comparisons
- Error reports with context

## Contributing

When adding new scripts:
1. Follow the established naming convention
2. Include comprehensive docstrings
3. Add error handling and logging
4. Update this README.md
5. Add usage examples
6. Include requirements documentation

## Security Notes

- **Credentials:** Never commit API credentials to version control
- **Responses:** Review collected API responses for sensitive data before committing
- **Environment:** Use `.env` files for local development, environment variables for CI/CD
- **Rate Limits:** Respect OFSC API rate limits in collection scripts

---

*Last updated: July 24, 2025*  
*Scripts are maintained as part of the pyOFSC v3.0 development effort*