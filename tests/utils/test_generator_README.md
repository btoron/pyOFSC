# OFSC Test Template Generator

The OFSC Test Template Generator is a powerful tool that automatically generates comprehensive test files for OFSC API endpoints based on the swagger specification and endpoint registry.

## Features

### 🔄 **Complete CRUD Operation Testing**
- **Create Operations**: Tests for POST/PUT endpoints with resource creation
- **Read Operations**: Tests for GET endpoints (individual and list operations)
- **Update Operations**: Tests for PUT/PATCH endpoints with data modification
- **Delete Operations**: Tests for DELETE endpoints with proper cleanup verification

### 🎯 **Parameter Boundary Testing**
- **Length Boundaries**: Tests for `min_length` and `max_length` constraints
- **Numeric Boundaries**: Tests for `minimum` and `maximum` value constraints
- **Enum Validation**: Tests for valid and invalid enum values
- **Type Validation**: Tests for parameter type enforcement

### ❌ **Negative Test Cases**
- **Not Found Tests**: Tests with non-existent resource IDs
- **Invalid Parameter Tests**: Tests with malformed or invalid parameters
- **Invalid Request Body Tests**: Tests with malformed request bodies for POST/PUT/PATCH endpoints

### 🔍 **Search and Filter Testing**
- **Search Functionality**: Tests for search parameters and query terms
- **Filter Combinations**: Tests for various filter parameter combinations
- **Edge Case Searches**: Tests for empty queries, wildcards, and special characters

### 📄 **Pagination Testing**
- **Page Size Validation**: Tests for different `limit` values
- **Offset Validation**: Tests for pagination traversal
- **Complete Pagination**: Tests for retrieving all pages of data
- **Boundary Pagination**: Tests for edge cases (empty results, single item, etc.)

### ⚡ **Performance Testing**
- **Individual Operation Performance**: Response time validation for each operation
- **Bulk Operation Performance**: Tests for multiple sequential operations
- **Concurrent Access Tests**: Tests for concurrent API access patterns
- **Rate Limiting Compliance**: Built-in rate limiting to avoid API throttling

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Generate tests for a specific resource
python scripts/generate_tests.py properties

# Generate tests with custom output path
python scripts/generate_tests.py activities --output tests/custom/my_tests.py

# List all available resources
python scripts/generate_tests.py --list

# Dry run to see what would be generated
python scripts/generate_tests.py users --dry-run
```

#### Advanced Options
```bash
# Verbose output with detailed information
python scripts/generate_tests.py properties --verbose

# See available resources organized by module
python scripts/generate_tests.py --list
```

### Programmatic Usage
```python
from tests.utils.test_generator import TestTemplateGenerator

# Create generator instance
generator = TestTemplateGenerator()

# Generate test file
output_file = generator.generate_test_file('properties')
print(f"Generated: {output_file}")

# Analyze available resources
endpoints = generator.find_resource_endpoints('activities')
crud_pattern = generator.get_crud_pattern('activities')
```

## Generated Test Structure

### File Organization
Each generated test file follows this structure:

```python
"""
Generated tests for <Resource> API endpoints.
Comprehensive test coverage including CRUD, validation, and performance tests.
"""

# Standard imports and setup
import pytest
from tests.utils.base_test import BaseOFSCTest

class Test<Resource>API(BaseOFSCTest):
    """Comprehensive tests for <Resource> API endpoints."""
    
    # Setup and configuration
    @pytest.fixture(autouse=True)
    async def setup_client(self, async_client):
        """Setup OFSC client and rate limiting."""
    
    # Helper methods
    def _create_test_<resource>_data(self, **overrides):
        """Create test data with unique identifiers."""
    
    def _validate_<resource>_response(self, response_data):
        """Validate response structure and content."""
    
    # CRUD operation tests
    async def test_create_<resource>(self):
        """Test resource creation with cleanup tracking."""
    
    async def test_get_<resource>_by_id(self):
        """Test individual resource retrieval."""
    
    async def test_list_<resources>(self):
        """Test resource listing with pagination."""
    
    async def test_update_<resource>(self):
        """Test resource updates."""
    
    async def test_delete_<resource>(self):
        """Test resource deletion with verification."""
    
    # Parameter boundary tests
    async def test_<endpoint>_<param>_boundary_length(self):
        """Test parameter length constraints."""
    
    async def test_<endpoint>_<param>_boundary_numeric(self):
        """Test numeric parameter boundaries."""
    
    async def test_<endpoint>_<param>_enum(self):
        """Test enum parameter validation."""
    
    # Negative test cases
    async def test_<endpoint>_not_found(self):
        """Test with non-existent resources."""
    
    async def test_<endpoint>_invalid_params(self):
        """Test with invalid parameters."""
    
    async def test_<endpoint>_invalid_body(self):
        """Test with invalid request bodies."""
    
    # Search and filter tests
    async def test_<endpoint>_search(self):
        """Test search functionality."""
    
    async def test_<endpoint>_filter(self):
        """Test filtering capabilities."""
    
    # Pagination tests
    async def test_<endpoint>_pagination(self):
        """Test pagination traversal."""
    
    # Performance tests
    async def test_<endpoint>_bulk_performance(self):
        """Test bulk operation performance."""
    
    async def test_<endpoint>_concurrent(self):
        """Test concurrent access patterns."""
```

### Test Categories

#### 1. CRUD Operations
- **Resource Lifecycle**: Complete create → read → update → delete cycle
- **Automatic Cleanup**: All created resources are tracked and cleaned up
- **Data Validation**: Response models are validated against Pydantic schemas
- **Performance Tracking**: All operations are timed and validated

#### 2. Parameter Validation
- **Boundary Testing**: Min/max values, length constraints
- **Type Validation**: Correct data types for all parameters
- **Enum Validation**: Valid enum values and rejection of invalid ones
- **Required vs Optional**: Proper handling of required and optional parameters

#### 3. Error Handling
- **HTTP Error Codes**: Proper handling of 404, 400, 422, etc.
- **Exception Types**: Correct OFSC exception types are raised
- **Error Messages**: Validation of error message content
- **Recovery Testing**: System behavior after errors

#### 4. Search and Filtering
- **Query Syntax**: Support for various query formats
- **Filter Combinations**: Multiple filter parameters
- **Result Validation**: Filtered results match filter criteria
- **Performance**: Search and filter operation timing

#### 5. Pagination
- **Page Traversal**: Walking through all pages of results
- **Boundary Conditions**: Empty results, single page, large datasets
- **Consistency**: Same data across paginated requests
- **Performance**: Pagination operation timing

## Integration with BaseOFSCTest

All generated tests inherit from `BaseOFSCTest`, providing:

### Automatic Features
- **Resource Cleanup**: Automatic tracking and cleanup of created test resources
- **Performance Tracking**: Built-in performance monitoring for all operations
- **Rate Limiting**: Automatic rate limiting to prevent API throttling
- **Error Context**: Detailed error reporting with endpoint and request context
- **Unique Naming**: Collision-free test resource names

### Helper Methods Available
```python
# Resource management
self.track_resource(type, id, cleanup_function)
self.generate_unique_name(resource_type)
self.generate_unique_label(resource_type, max_length)

# Performance tracking
async with self.track_performance('operation_name'):
    # API operations
self.assert_response_time_acceptable('operation', max_seconds)

# Validation helpers  
self.validate_response_model(response_data, ModelClass)
self.assert_pydantic_model_valid(data, ModelClass)
self.assert_response_structure(response_data)

# Error handling
async with self.expect_exception(ExceptionClass, message_contains="text"):
    # Operations that should fail

# API context
async with self.api_call_context(endpoint_id=123):
    # Automatic rate limiting and context tracking
```

## Customization and Extension

### Modifying Generated Tests

1. **Add Resource-Specific Logic**: Update the `_create_test_<resource>_data()` method with proper field values
2. **Enhance Validation**: Extend `_validate_<resource>_response()` with resource-specific checks
3. **Implement TODO Items**: Replace `# TODO:` comments with actual API calls
4. **Add Domain Logic**: Include business-specific validation and test scenarios

### Example Customization

```python
def _create_test_property_data(self, **overrides) -> Dict[str, Any]:
    """Create test data for property with optional overrides."""
    data = {
        'label': self.generate_unique_label('property'),
        'name': f"Test Property {datetime.now().strftime('%H%M%S')}",
        'type': 'string',  # Add specific field
        'entity': 'activity',  # Add specific field
        'sharing': 'private',  # Add specific field
        'gui': 'text',  # Add specific field
    }
    data.update(overrides)
    return data

def _validate_property_response(self, response_data: Dict[str, Any]) -> None:
    """Validate property response structure."""
    # Standard validation
    assert 'label' in response_data, "Response missing 'label' field"
    assert 'name' in response_data, "Response missing 'name' field"
    
    # Property-specific validation
    assert 'type' in response_data, "Response missing 'type' field"
    assert 'entity' in response_data, "Response missing 'entity' field"
    assert response_data['type'] in ['string', 'number', 'boolean', 'date', 'datetime']
    assert response_data['entity'] in ['activity', 'resource', 'customer']
```

### Adding Custom Test Categories

```python
async def test_property_enumeration_values(self):
    """Test property enumeration value management."""
    # Create property with enumeration
    property_data = self._create_test_property_data(type='enum')
    
    created_property = await self.create_test_resource(
        'property',
        lambda: self.client.metadata.create_or_replace_property(
            property_data['label'], property_data
        ),
        lambda: self.client.metadata.delete_property(property_data['label'])
    )
    
    # Test enumeration values
    enum_values = ['value1', 'value2', 'value3']
    
    await self.client.metadata.set_enumeration_values(
        property_data['label'], enum_values
    )
    
    # Validate enumeration values were set
    retrieved_values = await self.client.metadata.get_enumeration_values(
        property_data['label']
    )
    
    assert len(retrieved_values.items) == len(enum_values)
    retrieved_labels = [item.label for item in retrieved_values.items]
    assert set(retrieved_labels) == set(enum_values)
```

## Best Practices

### 1. Review Generated Tests
- **Understand the Structure**: Review the generated file to understand test organization
- **Implement TODOs**: Replace placeholder TODO comments with actual implementation
- **Add Business Logic**: Include domain-specific validation and scenarios

### 2. Customize for Your Needs
- **Resource-Specific Data**: Update data creation methods with realistic test data
- **Validation Logic**: Enhance response validation with business rules
- **Performance Thresholds**: Adjust performance assertions based on your requirements

### 3. Maintain Test Quality
- **Regular Updates**: Regenerate tests when API specifications change
- **Test Data Management**: Ensure test data is realistic and covers edge cases
- **Performance Monitoring**: Monitor and adjust performance thresholds

### 4. Integration with CI/CD
- **Automated Generation**: Include test generation in your CI/CD pipeline
- **Test Categories**: Use pytest markers to run different test categories
- **Parallel Execution**: Leverage BaseOFSCTest's rate limiting for parallel runs

## Troubleshooting

### Common Issues

#### No Endpoints Found
```bash
❌ No endpoints found for resource: my_resource
💡 Use --list to see available resources
```
**Solution**: Check the exact resource name using `--list` option.

#### Import Errors in Generated Tests
```python
ModuleNotFoundError: No module named 'ofsc.models.metadata'
```
**Solution**: The generator extracts model names from endpoint schemas. You may need to:
1. Update import statements based on actual model locations
2. Add missing model classes to the appropriate modules
3. Check that response schema names match actual model class names

#### TODO Items Not Implemented
```python
# TODO: Add actual API call here
pass
```
**Solution**: Generated tests include TODO comments where you need to add actual API calls. Replace these with proper implementation:

```python
# Before (generated)
# TODO: Add actual API call here
pass

# After (implemented)
response = await self.client.metadata.get_properties(limit=limit, offset=offset)
self.validate_response_model(response.dict(), PropertyListResponse)
```

#### Performance Test Failures
```python
AssertionError: Average operation time too slow: 3.142s
```
**Solution**: Adjust performance thresholds based on your environment:
```python
# Adjust thresholds in performance tests
assert avg_time < 5.0, f"Average operation time too slow: {avg_time:.3f}s"  # Increased from 2.0
```

### Getting Help

1. **Check Available Resources**: Use `python scripts/generate_tests.py --list`
2. **Dry Run First**: Use `--dry-run` to see what would be generated
3. **Verbose Output**: Use `--verbose` for detailed generation information
4. **Review Examples**: Check the generated demo files for patterns

## Architecture

### Generator Components

#### TestTemplateGenerator
Main class that orchestrates test generation:
- **Endpoint Analysis**: Parses swagger data and endpoint registry
- **CRUD Detection**: Identifies CRUD patterns in endpoint groups
- **Test Generation**: Creates comprehensive test methods
- **File Generation**: Produces complete test files

#### CRUDPattern
Analyzes endpoint groups to identify CRUD operations:
- **Resource Grouping**: Groups related endpoints by base path
- **Operation Detection**: Identifies Create, Read, Update, Delete operations
- **Relationship Analysis**: Determines resource relationships and dependencies

#### Template Methods
Specialized generators for different test categories:
- **CRUD Tests**: `_generate_crud_tests()`
- **Parameter Tests**: `_generate_parameter_tests()`
- **Negative Tests**: `_generate_negative_tests()`
- **Search Tests**: `_generate_search_filter_tests()`
- **Pagination Tests**: `_generate_pagination_tests()`
- **Performance Tests**: `_generate_performance_tests()`

### Integration Points

#### Swagger Specification
- **Endpoint Registry**: Uses parsed swagger data for endpoint information
- **Parameter Details**: Extracts parameter constraints and validation rules
- **Schema Information**: Uses request/response schemas for model validation

#### BaseOFSCTest Integration
- **Inheritance**: All generated tests inherit from BaseOFSCTest
- **Automatic Setup**: Leverages BaseOFSCTest's automatic setup and cleanup
- **Performance Tracking**: Uses built-in performance monitoring
- **Rate Limiting**: Integrates with automatic rate limiting

---

*The Test Template Generator is part of the pyOFSC v3.0 testing framework, designed to provide comprehensive and maintainable test coverage for all OFSC API endpoints.*