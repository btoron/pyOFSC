# Claude Code Implementation Prompts

## Phase 1: Initial Setup

### Prompt 1.1: Create Project Structure
```
Create the test directory structure and initial configuration files for testing an Oracle Field Service API proxy library. 

The proxy library uses:
- httpx for async HTTP requests
- Pydantic for request/response models
- Basic Auth for authentication

Create:
1. Complete directory structure under `tests/`
2. requirements-test.txt with all testing dependencies
3. pytest.ini configuration
4. .env.test template
5. Initial conftest.py with basic fixtures

Follow Python testing best practices and include both unit and integration test directories.
```

### Prompt 1.2: Parse Swagger and Generate Endpoint List
```
Parse the provided swagger.json file and create a Python module that lists all available endpoints with their:
- HTTP method
- Path template
- Required parameters
- Optional parameters
- Request body schema
- Response schema
- Rate limits (if specified)

Output this as a structured Python file at tests/fixtures/endpoints_registry.py that can be imported by other test modules.
```

## Phase 2: Base Infrastructure

### Prompt 2.1: Implement Base Test Class
```
Create a base test class at tests/utils/base_test.py that provides:

1. Automatic resource cleanup tracking
2. Error reporting with detailed context
3. Response model validation helpers
4. Performance tracking
5. Unique name generation for test resources
6. Rate limiting support

The class should be inherited by all endpoint test classes and handle common testing patterns.
```

### Prompt 2.2: Create Parameter Testing Framework
```
Create a parameter testing framework at tests/utils/parameter_testing.py that includes:

1. Data classes for test cases (ParameterTestCase, EndpointTestSuite)
2. Parameter generators for:
   - String boundaries (empty, max length, special chars, unicode)
   - Numeric boundaries (min, max, zero, negative)
   - Date boundaries (past, future, invalid formats)
   - Array boundaries (empty, max items)
3. Pairwise combination generator
4. Endpoint-specific parameter generators

Include proper type hints and documentation.
```

## Phase 3: Endpoint Test Implementation

### Prompt 3.1: Generate Test Template
```
Using the swagger file and the endpoint registry, create a test template generator that:

1. Takes an endpoint name as input
2. Generates a complete test file with:
   - All CRUD operations (if applicable)
   - Boundary test cases for each parameter
   - Negative test cases
   - Search/filter tests (for GET endpoints)
   - Pagination tests (if applicable)

Save the generator as tests/utils/test_generator.py
```

### Prompt 3.2: Implement Activity Endpoint Tests
```
Using the test template and the actual swagger definition for the activities endpoint, create comprehensive tests at tests/integration/test_endpoints/test_activities.py

Include:
1. Complete CRUD operation tests
2. All parameter boundary tests
3. Search and filter tests
4. Pagination tests
5. Concurrent operation tests
6. Special character handling tests

Use the parameter testing framework and base test class.
```

## Phase 4: Mock and Unit Tests

### Prompt 4.1: Create Mock Response Fixtures
```
Based on the swagger file, create mock response fixtures for all endpoints at tests/fixtures/responses/

Each file should contain:
1. Valid success responses
2. Common error responses (400, 401, 404, 500)
3. Edge case responses (empty lists, maximum data)

Format as Python dictionaries that match the Pydantic response models.
```

### Prompt 4.2: Implement Unit Tests
```
Create unit tests for the activities endpoint at tests/unit/test_endpoints/test_activities.py that:

1. Mock all HTTP calls using respx
2. Test request serialization
3. Test response parsing
4. Test error handling
5. Test retry logic
6. Run without any network calls

Use the mock fixtures created earlier.
```

## Phase 5: Advanced Features

### Prompt 5.1: Implement Rate Limiting Tests
```
Create tests that verify rate limiting works correctly:

1. Test concurrent requests respect the 10-request limit
2. Test rate limit errors are handled properly
3. Test request queuing and retry behavior
4. Create a rate limit test utility that can be reused

Save as tests/integration/test_rate_limiting.py
```

### Prompt 5.2: Create Data-Driven Tests
```
Create a data-driven test framework that:

1. Loads test cases from JSON files
2. Supports parameterized test execution
3. Generates test reports with parameter coverage
4. Can be extended with new test cases without code changes

Include example JSON test files for the activities endpoint.
```

## Phase 6: Utilities and Helpers

### Prompt 6.1: Create Test Data Generator
```
Create a test data generator at tests/utils/data_generator.py that:

1. Generates valid test data for all endpoints
2. Creates related data (e.g., customer for activity)
3. Supports different scenarios (minimal, full, boundary)
4. Integrates with Faker for realistic data
5. Ensures data consistency across related entities
```

### Prompt 6.2: Create Swagger Validator
```
Create a swagger validation utility that:

1. Validates all responses against the swagger schema
2. Reports schema mismatches
3. Can be used as a pytest fixture
4. Supports multiple API versions

This ensures the proxy correctly implements the API specification.
```

## Phase 7: Reporting and CI/CD

### Prompt 7.1: Create Test Report Generator
```
Create a test report generator that:

1. Produces HTML reports with parameter coverage
2. Shows endpoint test coverage
3. Tracks test execution time trends
4. Highlights slow or flaky tests
5. Generates actionable improvement suggestions

Output reports to reports/ directory.
```

### Prompt 7.2: Create GitHub Actions Workflow
```
Create a GitHub Actions workflow that:

1. Runs unit tests on every push
2. Runs integration tests on PR
3. Generates and uploads test reports
4. Fails if coverage drops below 80%
5. Runs different test suites in parallel
6. Notifies on test failures

Save as .github/workflows/test.yml
```

## Phase 8: Maintenance Tools

### Prompt 8.1: Create Test Maintenance Scripts
```
Create maintenance scripts in tests/scripts/ for:

1. Refreshing test data in sandbox
2. Cleaning up orphaned test resources
3. Syncing tests with swagger updates
4. Analyzing test failure patterns
5. Generating test documentation

Make them executable from command line.
```

### Prompt 8.2: Create Debugging Helpers
```
Create debugging utilities that:

1. Capture and replay failed API calls
2. Generate curl commands for failed requests
3. Compare expected vs actual responses
4. Provide detailed diff output
5. Support interactive debugging mode

These should help quickly diagnose test failures.
```

## Usage Instructions

### For each prompt:
1. Copy the prompt to Claude Code
2. Provide any additional context (swagger file, existing code)
3. Review and test the generated code
4. Iterate if adjustments are needed

### Execution order:
1. Complete Phase 1 entirely first
2. Phases 2-3 can be done in parallel
3. Phase 4 depends on Phases 1-3
4. Phases 5-8 can be done as needed

### Testing the tests:
After implementing each phase, verify:
```bash
# Run unit tests
pytest tests/unit -v

# Run integration tests for specific endpoint
pytest tests/integration/test_endpoints/test_activities.py -v

# Run with coverage
pytest --cov=oracle_field_service_proxy --cov-report=html

# Run specific test category
pytest -m "boundary" -v
```