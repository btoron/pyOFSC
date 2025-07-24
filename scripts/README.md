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
Parses swagger.json to generate a comprehensive endpoints registry with implementation detection.

**Purpose:** Creates a structured Python module containing all OFSC API endpoints with their metadata, parameters, schemas, and implementation status by analyzing the actual client API code.

**Usage:**
```bash
uv run python scripts/extract_endpoints.py
```

**Output:** Generates `tests/fixtures/endpoints_registry.py` with:
- Complete endpoint information (242 endpoints)
- HTTP methods, paths, and parameters
- Request/response schema references
- Implementation detection and method signatures
- Module organization (metadata, core, capacity, etc.)
- Utility functions for endpoint lookups

**Advanced Features:**
- **Implementation Detection**: Uses AST parsing to find actual method implementations
- **HTTP Method Semantics**: Intelligently maps endpoints to methods based on REST conventions
- **Parameter Normalization**: Handles parameter naming variations (snake_case ↔ camelCase, encoded prefixes)
- **Signature Generation**: Creates accurate method signatures from implemented code
- **Multi-pattern Endpoint Matching**: Supports f-strings, format strings, and direct assignments
- **Response Model Mapping**: Maps swagger schemas to Pydantic model classes

**Implementation Coverage Analysis:**
```
Module contains 242 endpoints across modules:
  auth: 2 endpoints (0 implemented, 0.0%)
  capacity: 11 endpoints (7 implemented, 63.6%)
  collaboration: 7 endpoints (0 implemented, 0.0%)
  core: 127 endpoints (103 implemented, 81.1%)
  metadata: 86 endpoints (49 implemented, 57.0%)
  partscatalog: 3 endpoints (0 implemented, 0.0%)
  statistics: 6 endpoints (0 implemented, 0.0%)

Implementation Summary:
  Total endpoints: 242
  Implemented endpoints: 159
  Implementation coverage: 65.7%
```

**Generated Module Usage:**
```python
from tests.fixtures.endpoints_registry import *

# Get endpoint by ID with implementation info
endpoint = get_endpoint_by_id(1)
print(f"{endpoint.method} {endpoint.path}")
print(f"Implemented: {bool(endpoint.implemented_in)}")
print(f"Signature: {endpoint.signature}")

# Find endpoint by method and path
endpoint = find_endpoint('GET', '/rest/ofscMetadata/v1/properties')

# Get all endpoints for a module
metadata_endpoints = get_endpoints_by_module('metadata')

# Filter by implementation status
implemented = [e for e in ENDPOINTS if e.implemented_in]
unimplemented = [e for e in ENDPOINTS if not e.implemented_in]

# Statistics
print(f"Total endpoints: {TOTAL_ENDPOINTS}")
print(f"By module: {ENDPOINTS_COUNT_BY_MODULE}")
print(f"Implementation coverage: {len(implemented)/len(ENDPOINTS)*100:.1f}%")
```

#### `compare_endpoints_sources.py`
Compares the endpoint registry with ENDPOINTS.md documentation to identify discrepancies.

**Purpose:** Validates implementation accuracy by comparing detected implementations with documented endpoint signatures and status.

**Usage:**
```bash
uv run python scripts/compare_endpoints_sources.py
```

**Output Example:**
```
================================================================================
🔍 ENDPOINTS COMPARISON REPORT
================================================================================
Comparing ENDPOINTS.md with endpoints_registry.py

📋 Loaded 242 endpoints from ENDPOINTS.md
📋 Loaded 242 endpoints from registry

🚨 ID 18: GET /rest/ofscMetadata/v1/capacityAreas/{label}/workZones (metadata)
   ❌ Doc shows implemented (version: DEPRECATED) but registry shows not implemented

🚨 ID 168: PUT /rest/ofscCore/v1/resources/{resourceId} (core)
   ✅ Registry shows implemented (core_api.py:OFSCoreAPI.update_resource()) but doc shows not implemented
   📝 Registry has signature but doc missing: async def update_resource(self, resource_id: str, resource_data: dict) -> Resource

================================================================================
📊 SUMMARY REPORT
================================================================================
Total endpoints compared: 242
Endpoints with issues: 2
Total issues found: 3

Issue breakdown:
  📋 Missing in ENDPOINTS.md: 0
  🗂️ Missing in registry: 0
  💻 Implementation discrepancies: 2
  📝 Signature discrepancies: 1

⚠️ Found 3 discrepancies that need attention.
```

**Issue Types Detected:**
- **Implementation Discrepancies**: Methods documented as implemented but not detected, or vice versa
- **Signature Mismatches**: Different method signatures between documentation and actual implementation
- **Missing Documentation**: Implemented methods not documented in ENDPOINTS.md
- **HTTP Method Misalignment**: PUT/PATCH/POST methods mapped to incorrect method types

**Features:**
- **Comprehensive Validation**: Compares all 242 endpoints for implementation status and signatures
- **Detailed Issue Reporting**: Provides specific file references and line numbers for fixes
- **Positive Findings**: Identifies implemented functionality not reflected in documentation
- **HTTP Method Validation**: Ensures proper REST semantic mapping (PUT→create, PATCH→update)
- **Progress Tracking**: Shows improvement over time (99.1% issue reduction achieved!)

**Development Workflow Integration:**
```bash
# 1. Update implementation
# 2. Regenerate registry
uv run python scripts/extract_endpoints.py

# 3. Compare and validate
uv run python scripts/compare_endpoints_sources.py > logs/comparison_$(date +%Y%m%d_%H%M%S).md

# 4. Review discrepancies and iterate
```

#### `generate_model_validation_tests.py`
Generates comprehensive validation tests for Pydantic models using real API response examples.

**Purpose:** Automatically creates model validation tests that ensure Pydantic models correctly parse real API responses, providing comprehensive coverage against authentic data.

**Usage:**
```bash
# Generate validation tests for all modules
uv run python scripts/generate_model_validation_tests.py

# Generate tests for specific module only
uv run python scripts/generate_model_validation_tests.py --module core
uv run python scripts/generate_model_validation_tests.py --module metadata
uv run python scripts/generate_model_validation_tests.py --module capacity

# Show coverage summary report
uv run python scripts/generate_model_validation_tests.py --summary

# Custom output directory
uv run python scripts/generate_model_validation_tests.py --output-dir tests/models/custom
```

**Key Features:**
- **Real Response Integration**: Uses saved API responses from `response_examples/` directory
- **Intelligent Model Mapping**: Extracts return types from endpoint signatures in the registry
- **Smart Import Resolution**: Maps model names to correct Pydantic classes automatically
- **List vs Single Response Handling**: Correctly validates both list responses and individual models
- **Comprehensive Coverage**: Generates tests for all models that have saved responses

**Coverage Analysis:**
```bash
uv run python scripts/generate_model_validation_tests.py --summary
================================================================================
MODEL VALIDATION TEST COVERAGE REPORT
================================================================================

Total models in registry: 344
Models with saved responses: 83 (24.1%)

Coverage by module:
  capacity: 0/15 (0.0%)
  core: 29/77 (37.7%)
  metadata: 45/65 (69.2%)
  statistics: 2/9 (22.2%)
```

**Generated Test Structure:**
```python
class TestCoreModelsValidation:
    """Test Core API model validation against response examples."""
    
    @pytest.fixture
    def response_examples_path(self):
        """Path to response examples directory."""
        return Path(__file__).parent.parent.parent.parent / "response_examples"

    def test_resource_validation(self, response_examples_path):
        """Validate Resource model against saved response examples."""
        response_files = ["167_get_resources_33015_33015.json"]
        
        for filename in response_files:
            with open(response_examples_path / filename) as f:
                data = json.load(f)
            
            if "_metadata" in data:
                del data["_metadata"]
            
            # Validate single response
            model_instance = Resource(**data)
            self._validate_resource_fields(model_instance, data)
            print(f"✅ Validated {filename}")

    def test_resource_list_response_validation(self, response_examples_path):
        """Validate ResourceListResponse model against saved response examples."""
        response_files = [
            "163_get_resources.json",
            "165_get_resources_FLUSA_descendants_FLUSA.json"
        ]
        
        for filename in response_files:
            with open(response_examples_path / filename) as f:
                data = json.load(f)
            
            if "_metadata" in data:
                del data["_metadata"]
            
            # Validate entire list response
            model_instance = ResourceListResponse(**data)
            self._validate_resource_list_response_fields(model_instance, data)
            print(f"✅ Validated {filename} as list response")
```

**Model Import Mapping:**
The script includes comprehensive model mappings for all modules:
```python
MODEL_IMPORT_MAP = {
    # Core models
    "Resource": "ofsc.models.core.Resource",
    "ResourceListResponse": "ofsc.models.core.ResourceListResponse",
    "Activity": "ofsc.models.core.Activity",
    "User": "ofsc.models.core.User",
    
    # Metadata models
    "ActivityTypeGroup": "ofsc.models.metadata.ActivityTypeGroup",
    "Property": "ofsc.models.metadata.Property",
    
    # Capacity models
    "CapacityResponse": "ofsc.models.capacity.CapacityResponse",
    # ... comprehensive mappings for all modules
}
```

**Smart Response Handling:**
- **List Responses**: Validates against `*ListResponse` models using full response data
- **Single Models**: Validates individual items against base model classes
- **Field Validation**: Includes model-specific field validation methods
- **Error Handling**: Gracefully skips missing files with informative messages

**Integration with Test Infrastructure:**
- **Uses Real Data**: Leverages the 98+ saved response examples collected systematically
- **Endpoint Context**: Maps responses back to specific endpoint IDs for traceability
- **Path Resolution**: Correctly resolves paths from test location to response examples
- **Pytest Integration**: Generated tests work seamlessly with existing test infrastructure

**Run Generated Tests:**
```bash
# Run all generated model validation tests
uv run pytest tests/models/generated/ -v

# Run specific module tests
uv run pytest tests/models/generated/test_core_models_validation.py -v

# Run specific model test
uv run pytest tests/models/generated/test_core_models_validation.py::TestCoreModelsValidation::test_resource_validation -v
```

**Development Workflow Integration:**
```bash
# 1. Collect API responses (already done - 98+ responses available)
uv run python scripts/collect_endpoint_response.py 220 --params william.arndt

# 2. Generate/regenerate model validation tests
uv run python scripts/generate_model_validation_tests.py

# 3. Run validation tests to ensure models work with real data
uv run pytest tests/models/generated/ -v

# 4. Check coverage and identify gaps
uv run python scripts/generate_model_validation_tests.py --summary
```

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
- `extract_endpoints.py` - Swagger parsing and registry generation with implementation detection
- `compare_endpoints_sources.py` - Registry validation and documentation comparison
- `generate_model_validation_tests.py` - Automated model validation test generation using real API responses

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
2. **Registry Generation:** Run `extract_endpoints.py` after swagger.json updates or implementation changes
3. **Validation:** Use `compare_endpoints_sources.py` to verify implementation accuracy and documentation sync
4. **Model Validation:** Generate model tests with `generate_model_validation_tests.py` using real responses
5. **Test Optimization:** Use `measure_test_performance.py` to benchmark changes
6. **CI/CD:** Use `run_tests_parallel.py` for optimized test execution

### Testing Workflow
1. Generate endpoint registry with `extract_endpoints.py`
2. Validate implementation accuracy with `compare_endpoints_sources.py`
3. Collect real responses with collection scripts for authentic test data
4. Generate automated model validation tests with `generate_model_validation_tests.py`
5. Run generated tests to ensure Pydantic models work with real API data
6. Measure baseline performance with `measure_test_performance.py`
7. Run optimized tests with `run_tests_parallel.py`

## Error Handling

All scripts include comprehensive error handling:
- **API Scripts:** Handle authentication failures, rate limits, network errors
- **Development Scripts:** Validate file paths, handle parsing errors
- **Test Scripts:** Graceful degradation, detailed error reporting

## Output Files

### Generated Files
- `tests/fixtures/endpoints_registry.py` - Complete endpoint registry with implementation detection
- `tests/models/generated/*.py` - Auto-generated model validation tests using real API responses
- `response_examples/*.json` - API response examples (98+ authentic responses)
- `logs/comparison_report_*.md` - Timestamped validation reports
- Performance measurement logs and reports

### Log Files
- Test execution logs with timestamps
- Endpoint comparison and validation reports
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