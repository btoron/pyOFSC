"""
Tests for the BaseOFSCTest utility class.

Verifies that the base test class provides all expected functionality.
"""

import asyncio
import json
import time
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from pydantic import BaseModel, ValidationError

from tests.utils.base_test import BaseOFSCTest, TestResourceTracker, PerformanceTracker, TestNameGenerator


class SimpleTestModel(BaseModel):
    """Simple test model for validation tests."""
    name: str
    value: int


class TestResourceTrackerUnit:
    """Test the TestResourceTracker utility class."""
    
    def test_track_resource(self):
        tracker = TestResourceTracker()
        
        # Track a resource
        tracker.track_resource('test_type', 'test_id', metadata='test')
        
        resources = tracker.get_resources()
        assert len(resources) == 1
        assert resources[0]['type'] == 'test_type'
        assert resources[0]['id'] == 'test_id'
        assert resources[0]['metadata'] == 'test'
        assert 'created_at' in resources[0]
    
    def test_get_resources_by_type(self):
        tracker = TestResourceTracker()
        
        tracker.track_resource('type1', 'id1')
        tracker.track_resource('type2', 'id2')
        tracker.track_resource('type1', 'id3')
        
        type1_resources = tracker.get_resources('type1')
        assert len(type1_resources) == 2
        assert all(r['type'] == 'type1' for r in type1_resources)
        
        type2_resources = tracker.get_resources('type2')
        assert len(type2_resources) == 1
        assert type2_resources[0]['type'] == 'type2'
    
    async def test_cleanup_all(self):
        tracker = TestResourceTracker()
        
        # Mock cleanup functions
        cleanup1 = AsyncMock()
        cleanup2 = Mock()
        
        tracker.track_resource('type1', 'id1', cleanup1)
        tracker.track_resource('type2', 'id2', cleanup2)
        
        # Execute cleanup
        await tracker.cleanup_all()
        
        # Verify cleanup functions were called
        cleanup1.assert_called_once()
        cleanup2.assert_called_once()
        
        # Verify resources were cleared
        assert len(tracker.get_resources()) == 0
        assert len(tracker.cleanup_functions) == 0
    
    async def test_cleanup_with_errors(self):
        tracker = TestResourceTracker()
        
        # Mock cleanup functions, one that raises exception
        cleanup1 = AsyncMock(side_effect=Exception("Cleanup error"))
        cleanup2 = Mock()
        
        tracker.track_resource('type1', 'id1', cleanup1)
        tracker.track_resource('type2', 'id2', cleanup2)
        
        # Cleanup should not raise exceptions
        await tracker.cleanup_all()
        
        # Both cleanup functions should have been called despite error
        cleanup1.assert_called_once()
        cleanup2.assert_called_once()
        
        # Resources should still be cleared
        assert len(tracker.get_resources()) == 0


class TestPerformanceTrackerUnit:
    """Test the PerformanceTracker utility class."""
    
    def test_operation_tracking(self):
        tracker = PerformanceTracker()
        
        tracker.start_operation('test_op')
        time.sleep(0.01)  # Small delay
        duration = tracker.end_operation('test_op')
        
        assert duration >= 0.01
        assert 'test_op' in tracker.metrics
        assert len(tracker.metrics['test_op']) == 1
    
    async def test_context_manager_tracking(self):
        tracker = PerformanceTracker()
        
        async with tracker.track_operation('test_context'):
            await asyncio.sleep(0.01)
        
        metrics = tracker.get_metrics()
        assert 'test_context' in metrics
        assert metrics['test_context']['count'] == 1
        assert metrics['test_context']['total'] >= 0.01
    
    def test_multiple_operations(self):
        tracker = PerformanceTracker()
        
        # Track same operation multiple times
        for i in range(3):
            tracker.start_operation('multi_op')
            time.sleep(0.005)
            tracker.end_operation('multi_op')
        
        metrics = tracker.get_metrics()
        multi_metrics = metrics['multi_op']
        
        assert multi_metrics['count'] == 3
        assert multi_metrics['total'] >= 0.015
        assert multi_metrics['average'] >= 0.005
        assert multi_metrics['min'] >= 0.004  # Allow some variance
        assert multi_metrics['max'] <= 0.1    # Reasonable upper bound
    
    def test_assert_performance(self):
        tracker = PerformanceTracker()
        
        tracker.start_operation('fast_op')
        time.sleep(0.01)
        tracker.end_operation('fast_op')
        
        # Should pass
        tracker.assert_performance('fast_op', 0.1)
        
        # Should fail
        with pytest.raises(AssertionError, match="exceeds maximum"):
            tracker.assert_performance('fast_op', 0.005)
    
    def test_operation_not_started_error(self):
        tracker = PerformanceTracker()
        
        with pytest.raises(ValueError, match="was not started"):
            tracker.end_operation('non_existent')


class TestNameGeneratorUnit:
    """Test the TestNameGenerator utility class."""
    
    def test_generate_name(self):
        generator = TestNameGenerator('TestClass', 'test_method')
        
        name1 = generator.generate_name('resource')
        name2 = generator.generate_name('resource')
        
        # Names should be unique
        assert name1 != name2
        
        # Names should contain expected components
        assert 'resource' in name1
        assert 'TestClass' in name1
        assert 'test_method' in name1
        assert 'test_' in name1  # default prefix
    
    def test_generate_name_with_prefix(self):
        generator = TestNameGenerator('TestClass', 'test_method')
        
        name = generator.generate_name('resource', 'custom')
        
        assert 'custom_' in name
        assert 'resource' in name
    
    def test_generate_label_with_length_constraint(self):
        generator = TestNameGenerator('VeryLongTestClassName', 'very_long_test_method_name')
        
        # Generate label with short length limit
        label = generator.generate_label('resource', max_length=20)
        
        assert len(label) <= 20
        assert 'resource' in label or 'res' in label  # Should contain resource type
    
    def test_names_are_unique_across_instances(self):
        gen1 = TestNameGenerator('Class1', 'method1')
        gen2 = TestNameGenerator('Class2', 'method2')
        
        name1 = gen1.generate_name('resource')
        name2 = gen2.generate_name('resource')
        
        assert name1 != name2


class TestBaseOFSCTestClass(BaseOFSCTest):
    """Test the BaseOFSCTest class functionality."""
    
    def test_setup_method_initialization(self):
        """Test that setup_method initializes all utilities correctly."""
        # Verify all utilities are initialized
        assert hasattr(self, 'resource_tracker')
        assert hasattr(self, 'performance_tracker')
        assert hasattr(self, 'name_generator')
        assert hasattr(self, 'test_context')
        
        # Verify context is populated
        assert self.test_context['test_class'] == 'TestBaseOFSCTestClass'
        assert self.test_context['test_method'] == 'test_setup_method_initialization'
        assert 'start_time' in self.test_context
    
    def test_unique_name_generation(self):
        """Test unique name generation."""
        name1 = self.generate_unique_name('test_resource')
        name2 = self.generate_unique_name('test_resource')
        
        assert name1 != name2
        assert 'test_resource' in name1
        assert 'test_resource' in name2
    
    def test_unique_label_generation(self):
        """Test unique label generation with constraints."""
        label1 = self.generate_unique_label('resource')
        label2 = self.generate_unique_label('resource', max_length=15)
        
        assert label1 != label2
        assert len(label2) <= 15
    
    def test_resource_tracking(self):
        """Test resource tracking functionality."""
        cleanup_mock = Mock()
        
        self.track_resource('test_type', 'test_id', cleanup_mock, extra='data')
        
        resources = self.resource_tracker.get_resources()
        assert len(resources) == 1
        assert resources[0]['type'] == 'test_type'
        assert resources[0]['id'] == 'test_id'
        assert resources[0]['extra'] == 'data'
    
    async def test_performance_tracking_context(self):
        """Test performance tracking context manager."""
        async with self.track_performance('test_operation'):
            await asyncio.sleep(0.01)
        
        metrics = self.get_performance_summary()
        assert 'test_operation' in metrics
        assert metrics['test_operation']['count'] == 1
        assert metrics['test_operation']['total'] >= 0.01
    
    def test_performance_assertion(self):
        """Test performance assertion functionality."""
        # Manually add a metric
        self.performance_tracker.metrics['test_op'] = [0.05]
        
        # Should pass
        self.assert_performance_within_limits('test_op', 0.1)
        
        # Should fail
        with pytest.raises(AssertionError):
            self.assert_performance_within_limits('test_op', 0.01)
    
    def test_response_time_assertion(self):
        """Test response time assertion convenience method."""
        # Manually add a metric
        self.performance_tracker.metrics['api_call'] = [0.5]
        
        # Should pass
        self.assert_response_time_acceptable('api_call', max_seconds=1.0)
        
        # Should fail
        with pytest.raises(AssertionError):
            self.assert_response_time_acceptable('api_call', max_seconds=0.1)
    
    def test_rate_limiting_configuration(self):
        """Test rate limiting configuration."""
        # Test setting custom delay
        self.set_rate_limit_delay(0.5)
        assert self.rate_limit_delay == 0.5
        
        # Test default delay
        self.set_rate_limit_delay(0.0)
        assert self.rate_limit_delay == 0.0
    
    async def test_rate_limiting_behavior(self):
        """Test rate limiting behavior."""
        self.set_rate_limit_delay(0.1)
        
        start_time = time.time()
        
        # Make multiple calls that should be rate limited
        for _ in range(3):
            await self.respect_rate_limits()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should take at least 0.2 seconds (2 delays of 0.1s each)
        assert total_time >= 0.15  # Allow some variance
    
    def test_pydantic_model_validation_success(self):
        """Test successful Pydantic model validation."""
        data = {'name': 'test', 'value': 42}
        
        model = self.assert_pydantic_model_valid(data, SimpleTestModel)
        
        assert isinstance(model, SimpleTestModel)
        assert model.name == 'test'
        assert model.value == 42
    
    def test_pydantic_model_validation_failure(self):
        """Test Pydantic model validation failure."""
        data = {'name': 'test', 'value': 'not_an_int'}
        
        with pytest.raises(AssertionError, match="Data validation failed"):
            self.assert_pydantic_model_valid(data, SimpleTestModel)
    
    def test_endpoint_context_setting(self):
        """Test setting endpoint context."""
        # Test setting by ID (would need real endpoint registry)
        # For now, test setting by endpoint info object
        from tests.fixtures.endpoints_registry import EndpointInfo
        
        endpoint_info = EndpointInfo(
            id=1,
            path='/test/path',
            method='GET',
            module='test',
            summary='Test endpoint',
            description='Test description',
            operation_id='test_op',
            tags=['test'],
            required_parameters=[],
            optional_parameters=[],
            request_body_schema=None,
            response_schema='TestResponse'
        )
        
        self.set_endpoint_context(endpoint_info=endpoint_info)
        
        assert self.test_context['endpoint_info'] is not None
        assert self.test_context['endpoint_info']['id'] == 1
        assert self.test_context['endpoint_info']['path'] == '/test/path'
        assert self.test_context['endpoint_info']['method'] == 'GET'
    
    def test_request_context_tracking(self):
        """Test request context tracking."""
        self.add_request_context(
            'GET', 
            'https://api.example.com/test',
            params={'test': 'value'},
            headers={'Authorization': 'Bearer secret', 'Content-Type': 'application/json'}
        )
        
        requests = self.test_context['requests_made']
        assert len(requests) == 1
        
        request = requests[0]
        assert request['method'] == 'GET'
        assert request['url'] == 'https://api.example.com/test'
        assert request['params'] == {'test': 'value'}
        
        # Authorization header should be filtered out
        assert 'authorization' not in request['headers']
        assert 'Content-Type' in request['headers']
    
    def test_response_context_tracking(self):
        """Test response context tracking."""
        # Test with dict response
        response_data = {'status': 'success', 'data': [1, 2, 3]}
        self.add_response_context(response_data, status_code=200)
        
        responses = self.test_context['responses_received']
        assert len(responses) == 1
        
        response = responses[0]
        assert response['status_code'] == 200
        assert response['data_keys'] == ['status', 'data']
    
    async def test_api_call_context_manager(self):
        """Test API call context manager."""
        # Mock an API call
        start_time = time.time()
        
        async with self.api_call_context(operation_name='test_api'):
            await asyncio.sleep(0.01)
        
        end_time = time.time()
        
        # Should have tracked performance
        metrics = self.get_performance_summary()
        assert 'test_api' in metrics
        
        # Should have applied rate limiting (if configured)
        if self.rate_limit_delay > 0:
            assert (end_time - start_time) >= self.rate_limit_delay
    
    async def test_expect_exception_context_manager(self):
        """Test exception expectation context manager."""
        # Test successful exception catching
        async with self.expect_exception(ValueError, message_contains="test error"):
            raise ValueError("This is a test error message")
        
        # Test failure when no exception is raised
        with pytest.raises(AssertionError, match="Expected ValueError but no exception"):
            async with self.expect_exception(ValueError):
                pass
        
        # Test failure when wrong exception type is raised
        with pytest.raises(AssertionError, match="Expected ValueError but got RuntimeError"):
            async with self.expect_exception(ValueError):
                raise RuntimeError("Wrong exception type")
        
        # Test failure when exception message doesn't contain expected text
        with pytest.raises(AssertionError, match="does not contain"):
            async with self.expect_exception(ValueError, message_contains="expected text"):
                raise ValueError("This doesn't have the expected content")
    
    async def test_create_test_resource_functionality(self):
        """Test create_test_resource helper method."""
        cleanup_called = False
        
        async def create_function(name, value=42):
            return SimpleTestModel(name=name, value=value)
        
        async def cleanup_function():
            nonlocal cleanup_called
            cleanup_called = True
        
        # Create resource
        resource = await self.create_test_resource(
            resource_type='test_model',
            create_function=create_function,
            cleanup_function=cleanup_function,
            name='test_resource',
            value=100
        )
        
        # Verify resource was created correctly
        assert isinstance(resource, SimpleTestModel)
        assert resource.name == 'test_resource'
        assert resource.value == 100
        
        # Verify resource was tracked
        resources = self.resource_tracker.get_resources('test_model')
        assert len(resources) == 1
        
        # Cleanup should be tracked but not yet called
        assert not cleanup_called
        assert len(self.resource_tracker.cleanup_functions) == 1
        
        # Manual cleanup to test
        await self.resource_tracker.cleanup_all()
        assert cleanup_called