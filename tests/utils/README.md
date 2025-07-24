# OFSC Test Utilities

This directory contains utility classes and helpers for testing the OFSC Python Wrapper v3.0.

## Overview

The test utilities provide a comprehensive framework for testing OFSC API endpoints with features like automatic resource cleanup, performance tracking, response validation, and error reporting.

## Files

### `base_test.py` - BaseOFSCTest Class

The main base test class that all endpoint test classes should inherit from.

**Key Features:**
- **Automatic Resource Cleanup**: Tracks created resources and cleans them up automatically
- **Performance Tracking**: Measures and reports operation performance
- **Response Model Validation**: Validates API responses against Pydantic models
- **Error Reporting**: Provides detailed context for debugging test failures
- **Unique Name Generation**: Creates unique names for test resources
- **Rate Limiting Support**: Handles API rate limits intelligently

### `validation_helpers.py` - Response Validation Utilities

Helper functions for validating API responses and Pydantic models.

### `factories.py` - Test Data Factories

Factory functions for creating test data objects.

### `example_base_test_usage.py` - Usage Examples

Comprehensive examples showing how to use BaseOFSCTest effectively.

## Using BaseOFSCTest

### Basic Usage

```python
from tests.utils.base_test import BaseOFSCTest

class TestMyEndpoint(BaseOFSCTest):
    @pytest.fixture(autouse=True)
    async def setup_client(self, async_client):
        self.client = async_client
    
    async def test_my_endpoint(self):
        # Set endpoint context for error reporting
        self.set_endpoint_context(endpoint_id=50)
        
        # Make API call with performance tracking
        async with self.track_performance('api_call'):
            response = await self.client.metadata.get_properties()
        
        # Validate response
        self.validate_response_model(response.dict(), PropertyListResponse)
        
        # Assert performance
        self.assert_response_time_acceptable('api_call', max_seconds=2.0)
```

### Resource Management

```python
async def test_create_resource_with_cleanup(self):
    # Generate unique name
    property_label = self.generate_unique_label('property')
    
    # Define cleanup function
    async def cleanup():
        try:
            await self.client.metadata.delete_property(property_label)
        except OFSNotFoundException:
            pass
    
    # Create resource with automatic cleanup tracking
    property_obj = await self.create_test_resource(
        resource_type='property',
        create_function=lambda: self.client.metadata.create_property(
            property_label, property_data
        ),
        cleanup_function=cleanup
    )
    
    # Test the created resource...
    # Cleanup happens automatically in teardown_method
```

### Performance Tracking

```python
async def test_with_performance_tracking(self):
    # Track individual operations
    async with self.track_performance('operation1'):
        await self.client.some_operation()
    
    async with self.track_performance('operation2'):
        await self.client.another_operation()
    
    # Get performance summary
    metrics = self.get_performance_summary()
    
    # Assert performance requirements
    self.assert_performance_within_limits('operation1', max_duration=1.0)
    self.assert_response_time_acceptable('operation2', max_seconds=0.5)
```

### Error Handling and Context

```python
async def test_error_handling_with_context(self):
    # Set endpoint context
    self.set_endpoint_context(endpoint_id=51)
    
    # Test expected exceptions
    async with self.expect_exception(OFSNotFoundException, message_contains="not found"):
        await self.client.metadata.get_property("nonexistent")
    
    # Add request/response context for debugging
    self.add_request_context('GET', '/api/endpoint', params={'test': 'value'})
    self.add_response_context(response_data, status_code=404)
```

### Rate Limiting

```python
async def test_with_rate_limiting(self):
    # Set custom rate limit
    self.set_rate_limit_delay(0.5)  # 500ms between requests
    
    # Make multiple requests with automatic rate limiting
    for i in range(3):
        async with self.api_call_context(operation_name=f'request_{i}'):
            await self.client.metadata.get_properties(offset=i)
```

### Validation Helpers

```python
async def test_response_validation(self):
    response = await self.client.metadata.get_properties()
    response_data = response.dict()
    
    # Validate response structure
    self.assert_response_structure(response_data)
    
    # Validate individual models
    properties = self.validate_list_response_models(
        response_data, 
        PropertyResponse,
        min_items=1
    )
    
    # Validate against Pydantic model
    self.assert_pydantic_model_valid(response_data, PropertyListResponse)
```

## Utility Classes

### TestResourceTracker

Automatically tracks and cleans up test resources.

**Methods:**
- `track_resource(type, id, cleanup_function, **metadata)` - Track a resource for cleanup
- `get_resources(type=None)` - Get tracked resources
- `cleanup_all()` - Execute all cleanup functions

### PerformanceTracker

Tracks operation performance and provides metrics.

**Methods:**
- `start_operation(name)` - Start tracking an operation
- `end_operation(name)` - End tracking and return duration
- `track_operation(name)` - Context manager for tracking
- `get_metrics()` - Get performance summary
- `assert_performance(name, max_duration)` - Assert performance limits

### TestNameGenerator

Generates unique names for test resources.

**Methods:**
- `generate_name(resource_type, prefix="test")` - Generate unique name
- `generate_label(resource_type, max_length=40)` - Generate unique label with length constraints

## Configuration

### Environment Variables

- `PYTEST_SAVE_PERFORMANCE=true` - Save performance metrics to files
- `PYTEST_RATE_LIMITED=true` - Enable rate limiting for tests
- `PYTEST_DISABLE_PARALLEL=true` - Disable parallel test execution

### Rate Limiting Configuration

Rate limiting is automatically configured based on test environment:
- **Live tests** (`--live` flag): 500ms delay between requests
- **Rate limited environment**: 200ms delay between requests  
- **Unit tests**: No rate limiting

## Integration with Pytest

### Automatic Setup

The base class includes an `autouse` fixture that automatically:
- Sets up rate limiting based on command line options
- Configures test environment detection
- Initializes all utility classes

### Fixtures Integration

```python
class TestExample(BaseOFSCTest):
    @pytest.fixture(autouse=True)
    async def setup_client(self, async_client):
        """Setup OFSC client."""
        self.client = async_client
    
    @pytest.fixture(autouse=True) 
    async def setup_test_data(self):
        """Setup shared test data with cleanup."""
        # Create shared resources that will be cleaned up automatically
        pass
```

### Debug Information

The base class automatically saves debug information on test failures:
- Test context with endpoint information
- Request/response details (without sensitive data)
- Performance metrics
- Error context and validation failures

Debug files are saved to `test_debug/` directory with unique names per test failure.

## Best Practices

### 1. Always Inherit from BaseOFSCTest

```python
# ✅ Good
class TestMyEndpoint(BaseOFSCTest):
    pass

# ❌ Bad
class TestMyEndpoint:
    pass
```

### 2. Set Endpoint Context

```python
async def test_endpoint(self):
    # ✅ Good - provides context for error reporting
    self.set_endpoint_context(endpoint_id=50)
    
    # Make API calls...
```

### 3. Use Resource Tracking

```python
async def test_create_resource(self):
    # ✅ Good - automatic cleanup
    resource = await self.create_test_resource(
        'property', 
        create_function, 
        cleanup_function
    )
    
    # ❌ Bad - manual cleanup required
    resource = await create_function()
    # ... test code ...
    await cleanup_function()  # Easy to forget or skip on failure
```

### 4. Track Performance for Critical Operations

```python
async def test_critical_operation(self):
    # ✅ Good - track performance of important operations
    async with self.track_performance('critical_op'):
        result = await self.client.important_operation()
    
    # Assert performance requirements
    self.assert_response_time_acceptable('critical_op', max_seconds=1.0)
```

### 5. Validate Response Models

```python
async def test_api_response(self):
    response = await self.client.get_data()
    
    # ✅ Good - validate response structure and models
    self.assert_response_structure(response.dict())
    self.validate_response_model(response.dict(), ExpectedModel)
    
    # ❌ Bad - no validation
    assert response is not None
```

## Error Handling

The base class provides comprehensive error handling:

### Exception Context Managers

```python
# Test expected exceptions with message validation
async with self.expect_exception(OFSNotFoundException, message_contains="not found"):
    await self.client.get_nonexistent_resource()
```

### Automatic Error Context

The base class automatically captures:
- Endpoint information
- Request details (sanitized)
- Response metadata
- Performance metrics
- Validation failures

This information is available in debug files when tests fail.

## Performance Testing

### Setting Performance Expectations

```python
async def test_performance_requirements(self):
    async with self.track_performance('list_properties'):
        await self.client.metadata.get_properties(limit=100)
    
    # Assert operation completed within time limit
    self.assert_performance_within_limits('list_properties', 2.0)
    
    # Or use convenience method
    self.assert_response_time_acceptable('list_properties', max_seconds=2.0)
```

### Batch Performance Testing

```python
async def test_batch_performance(self):
    async with self.track_performance('batch_operations'):
        for i in range(10):
            async with self.api_call_context():
                await self.client.get_item(i)
    
    metrics = self.get_performance_summary()
    batch_metrics = metrics['batch_operations']
    
    # Assert average performance
    assert batch_metrics['average'] < 1.0, f"Batch too slow: {batch_metrics['average']}s"
    
    # Assert total time reasonable
    assert batch_metrics['total'] < 15.0, f"Total time too long: {batch_metrics['total']}s"
```

## Migration from Existing Tests

To migrate existing test classes:

1. **Change inheritance**:
   ```python
   # Before
   class TestMetadata:
   
   # After  
   class TestMetadata(BaseOFSCTest):
   ```

2. **Add client setup fixture**:
   ```python
   @pytest.fixture(autouse=True)
   async def setup_client(self, async_client):
       self.client = async_client
   ```

3. **Replace manual cleanup with resource tracking**:
   ```python
   # Before
   async def test_create_property(self):
       prop = await self.client.create_property(data)
       try:
           # test code
           pass
       finally:
           await self.client.delete_property(prop.label)
   
   # After
   async def test_create_property(self):
       prop = await self.create_test_resource(
           'property',
           lambda: self.client.create_property(data),
           lambda: self.client.delete_property(prop.label)
       )
       # test code - cleanup automatic
   ```

4. **Add performance tracking for important operations**:
   ```python
   # Before
   response = await self.client.get_properties()
   
   # After
   async with self.track_performance('get_properties'):
       response = await self.client.get_properties()
   self.assert_response_time_acceptable('get_properties', max_seconds=2.0)
   ```

---

*For more examples and advanced usage patterns, see `example_base_test_usage.py`*