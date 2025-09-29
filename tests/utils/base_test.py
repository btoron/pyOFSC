"""
Base test class for OFSC API testing.

This module provides a comprehensive base test class that should be inherited by all
endpoint test classes. It handles common testing patterns including:

1. Automatic resource cleanup tracking
2. Error reporting with detailed context
3. Response model validation helpers
4. Performance tracking
5. Unique name generation for test resources
6. Rate limiting support

Usage:
    class TestMyEndpoint(BaseOFSCTest):
        async def test_my_endpoint(self):
            # Test implementation
            pass
"""

import asyncio
import json
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union, Callable

import pytest
from pydantic import BaseModel, ValidationError
from httpx import Response

from tests.utils.validation_helpers import (
    validate_model_from_response,
    validate_list_response,
    assert_base_response_fields,
    validate_error_response,
)
from tests.fixtures.endpoints_registry import EndpointInfo, get_endpoint_by_id


class TestResourceTracker:
    """Tracks test resources for automatic cleanup."""

    def __init__(self):
        self.resources: List[Dict[str, Any]] = []
        self.cleanup_functions: List[Callable] = []

    def track_resource(
        self,
        resource_type: str,
        resource_id: str,
        cleanup_function: Optional[Callable] = None,
        **metadata,
    ):
        """Track a resource for cleanup.

        Args:
            resource_type: Type of resource (e.g., 'activity', 'user', 'property')
            resource_id: Unique identifier for the resource
            cleanup_function: Function to call for cleanup (optional)
            **metadata: Additional metadata about the resource
        """
        resource = {
            "type": resource_type,
            "id": resource_id,
            "created_at": datetime.now(timezone.utc),
            "cleanup_function": cleanup_function,
            **metadata,
        }
        self.resources.append(resource)

        if cleanup_function:
            self.cleanup_functions.append(cleanup_function)

    def get_resources(
        self, resource_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get tracked resources, optionally filtered by type."""
        if resource_type:
            return [r for r in self.resources if r["type"] == resource_type]
        return self.resources.copy()

    async def cleanup_all(self):
        """Execute all cleanup functions."""
        cleanup_errors = []

        for cleanup_func in reversed(self.cleanup_functions):  # LIFO cleanup
            try:
                if asyncio.iscoroutinefunction(cleanup_func):
                    await cleanup_func()
                else:
                    cleanup_func()
            except Exception as e:
                cleanup_errors.append(f"Cleanup error: {e}")

        # Clear tracking after cleanup
        self.resources.clear()
        self.cleanup_functions.clear()

        if cleanup_errors:
            # Log cleanup errors but don't fail the test
            print(f"Warning: {len(cleanup_errors)} cleanup errors occurred:")
            for error in cleanup_errors:
                print(f"  - {error}")


class PerformanceTracker:
    """Tracks performance metrics for test operations."""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.operation_start_times: Dict[str, float] = {}

    def start_operation(self, operation_name: str):
        """Start tracking an operation."""
        self.operation_start_times[operation_name] = time.perf_counter()

    def end_operation(self, operation_name: str) -> float:
        """End tracking an operation and return duration."""
        if operation_name not in self.operation_start_times:
            raise ValueError(f"Operation '{operation_name}' was not started")

        start_time = self.operation_start_times.pop(operation_name)
        duration = time.perf_counter() - start_time

        if operation_name not in self.metrics:
            self.metrics[operation_name] = []
        self.metrics[operation_name].append(duration)

        return duration

    @asynccontextmanager
    async def track_operation(self, operation_name: str):
        """Context manager for tracking operations."""
        self.start_operation(operation_name)
        try:
            yield
        finally:
            self.end_operation(operation_name)

    def get_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics summary."""
        summary = {}
        for operation, durations in self.metrics.items():
            summary[operation] = {
                "count": len(durations),
                "total": sum(durations),
                "average": sum(durations) / len(durations),
                "min": min(durations),
                "max": max(durations),
            }
        return summary

    def assert_performance(self, operation_name: str, max_duration: float):
        """Assert that operation performance is within acceptable limits."""
        if operation_name not in self.metrics:
            raise ValueError(f"No metrics found for operation '{operation_name}'")

        durations = self.metrics[operation_name]
        avg_duration = sum(durations) / len(durations)

        assert avg_duration <= max_duration, (
            f"Operation '{operation_name}' average duration {avg_duration:.3f}s "
            f"exceeds maximum {max_duration:.3f}s"
        )


class TestNameGenerator:
    """Generates unique names for test resources."""

    def __init__(self, test_class_name: str, test_method_name: str):
        self.test_class = test_class_name
        self.test_method = test_method_name
        self.counter = 0
        self.session_id = uuid.uuid4().hex[:8]

    def generate_name(self, resource_type: str, prefix: str = "test") -> str:
        """Generate a unique name for a test resource.

        Args:
            resource_type: Type of resource (e.g., 'activity', 'user')
            prefix: Prefix for the name (default: 'test')

        Returns:
            Unique resource name
        """
        self.counter += 1
        timestamp = int(time.time())

        # Create a name that's unique and identifiable
        # Format: prefix_resourcetype_class_method_session_counter_timestamp
        name = (
            f"{prefix}_{resource_type}_{self.test_class}_{self.test_method}_"
            f"{self.session_id}_{self.counter}_{timestamp}"
        )

        # Truncate if too long (OFSC has limits on some resource names)
        if len(name) > 80:
            # Keep prefix, resource type, and unique parts
            name = (
                f"{prefix}_{resource_type}_{self.session_id}_{self.counter}_{timestamp}"
            )

        return name

    def generate_label(self, resource_type: str, max_length: int = 40) -> str:
        """Generate a unique label for resources with length constraints.

        Args:
            resource_type: Type of resource
            max_length: Maximum length for the label (default: 40 for OFSC)

        Returns:
            Unique resource label within length constraints
        """
        self.counter += 1

        # Use shorter format for labels
        base_name = f"{resource_type}_{self.session_id}_{self.counter}"

        if len(base_name) <= max_length:
            return base_name

        # If still too long, use minimal format
        minimal_name = f"{resource_type[:3]}_{self.counter}_{self.session_id[:4]}"

        if len(minimal_name) <= max_length:
            return minimal_name

        # Last resort: just use counter and session
        return f"{self.counter}_{self.session_id[:8]}"[:max_length]


class BaseOFSCTest:
    """
    Base test class for OFSC API testing.

    Provides comprehensive testing utilities including resource tracking,
    performance monitoring, validation helpers, and error reporting.

    All endpoint test classes should inherit from this class.
    """

    def setup_method(self, method):
        """Set up test method with all utilities."""
        self.test_class_name = self.__class__.__name__
        self.test_method_name = method.__name__

        # Initialize utilities
        self.resource_tracker = TestResourceTracker()
        self.performance_tracker = PerformanceTracker()
        self.name_generator = TestNameGenerator(
            self.test_class_name, self.test_method_name
        )

        # Test context for error reporting
        self.test_context = {
            "test_class": self.test_class_name,
            "test_method": self.test_method_name,
            "start_time": datetime.now(timezone.utc),
            "endpoint_info": None,
            "requests_made": [],
            "responses_received": [],
        }

        # Rate limiting state
        self.rate_limit_delay = 0.1  # Default delay between requests
        self.last_request_time = 0

    async def teardown_method(self, method):
        """Clean up after test method."""
        # Clean up tracked resources
        await self.resource_tracker.cleanup_all()

        # Save performance metrics if enabled
        if os.getenv("PYTEST_SAVE_PERFORMANCE", "").lower() in ("true", "1"):
            await self._save_performance_metrics()

        # Save test context on failure (handled by conftest.py)
        # method parameter is required by pytest but not used here
        _ = method

    # Resource Management Methods

    def track_resource(
        self,
        resource_type: str,
        resource_id: str,
        cleanup_function: Optional[Callable] = None,
        **metadata,
    ):
        """Track a resource for automatic cleanup.

        Args:
            resource_type: Type of resource
            resource_id: Resource identifier
            cleanup_function: Optional cleanup function
            **metadata: Additional resource metadata
        """
        self.resource_tracker.track_resource(
            resource_type, resource_id, cleanup_function, **metadata
        )

    def generate_unique_name(self, resource_type: str, prefix: str = "test") -> str:
        """Generate unique name for test resources."""
        return self.name_generator.generate_name(resource_type, prefix)

    def generate_unique_label(self, resource_type: str, max_length: int = 40) -> str:
        """Generate unique label for test resources."""
        return self.name_generator.generate_label(resource_type, max_length)

    # Performance Tracking Methods

    @asynccontextmanager
    async def track_performance(self, operation_name: str):
        """Track performance of an operation."""
        async with self.performance_tracker.track_operation(operation_name):
            yield

    def assert_performance_within_limits(
        self, operation_name: str, max_duration: float
    ):
        """Assert operation performance is within limits."""
        self.performance_tracker.assert_performance(operation_name, max_duration)

    def get_performance_summary(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics summary."""
        return self.performance_tracker.get_metrics()

    # Rate Limiting Support

    async def respect_rate_limits(self):
        """Apply rate limiting between requests."""
        if self.rate_limit_delay > 0:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time

            if time_since_last < self.rate_limit_delay:
                sleep_time = self.rate_limit_delay - time_since_last
                await asyncio.sleep(sleep_time)

            self.last_request_time = time.time()

    def set_rate_limit_delay(self, delay: float):
        """Set the delay between requests for rate limiting."""
        self.rate_limit_delay = delay

    # Response Validation Methods

    def validate_response_model(
        self,
        response_data: Dict[str, Any],
        model_class: Type[BaseModel],
        items_key: str = "items",
    ) -> bool:
        """Validate response data against a Pydantic model.

        Args:
            response_data: Response data to validate
            model_class: Pydantic model class
            items_key: Key for list items in response

        Returns:
            True if validation succeeds

        Raises:
            ValidationError: If validation fails
        """
        return validate_model_from_response(model_class, response_data, items_key)

    def validate_list_response_models(
        self,
        response_data: Dict[str, Any],
        model_class: Type[BaseModel],
        items_key: str = "items",
        min_items: Optional[int] = None,
    ) -> List[BaseModel]:
        """Validate and return list of models from response."""
        return validate_list_response(model_class, response_data, items_key, min_items)

    def assert_response_structure(self, response_data: Dict[str, Any]):
        """Assert response has expected base structure."""
        assert_base_response_fields(response_data)

    def validate_error_response(
        self,
        response_data: Dict[str, Any],
        expected_status: Optional[str] = None,
        expected_code: Optional[str] = None,
    ):
        """Validate error response structure."""
        validate_error_response(response_data, expected_status, expected_code)

    def assert_pydantic_model_valid(
        self, data: Dict[str, Any], model_class: Type[BaseModel]
    ) -> BaseModel:
        """Assert data is valid for a Pydantic model and return instance.

        Args:
            data: Data to validate
            model_class: Pydantic model class

        Returns:
            Validated model instance

        Raises:
            AssertionError: If validation fails with detailed message
        """
        try:
            return model_class(**data)
        except ValidationError as e:
            self._add_error_context(
                "model_validation_error",
                {
                    "model_class": model_class.__name__,
                    "validation_errors": e.errors(),
                    "invalid_data": data,
                },
            )
            raise AssertionError(
                f"Data validation failed for {model_class.__name__}: {e}"
            ) from e

    # Error Reporting and Context Methods

    def set_endpoint_context(
        self,
        endpoint_id: Optional[int] = None,
        endpoint_info: Optional[EndpointInfo] = None,
    ):
        """Set endpoint context for error reporting.

        Args:
            endpoint_id: Endpoint ID from ENDPOINTS.md
            endpoint_info: EndpointInfo object directly
        """
        if endpoint_id:
            endpoint_info = get_endpoint_by_id(endpoint_id)

        if endpoint_info:
            self.test_context["endpoint_info"] = {
                "id": endpoint_info.id,
                "path": endpoint_info.path,
                "method": endpoint_info.method,
                "module": endpoint_info.module,
                "summary": endpoint_info.summary,
            }

    def add_request_context(self, method: str, url: str, **kwargs):
        """Add request context for error reporting."""
        request_info = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": method,
            "url": url,
            "params": kwargs.get("params"),
            "headers": {
                k: v
                for k, v in kwargs.get("headers", {}).items()
                if k.lower() not in ["authorization"]
            },  # Don't log auth headers
        }
        self.test_context["requests_made"].append(request_info)

    def add_response_context(
        self,
        response: Union[Response, Dict[str, Any]],
        status_code: Optional[int] = None,
    ):
        """Add response context for error reporting."""
        if isinstance(response, Response):
            response_info = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "size": len(response.content) if hasattr(response, "content") else 0,
            }
        else:
            response_info = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status_code": status_code,
                "data_keys": list(response.keys())
                if isinstance(response, dict)
                else "non-dict",
                "size": len(str(response)),
            }

        self.test_context["responses_received"].append(response_info)

    def _add_error_context(self, error_type: str, context: Dict[str, Any]):
        """Add error context information."""
        if "errors" not in self.test_context:
            self.test_context["errors"] = []

        self.test_context["errors"].append(
            {
                "type": error_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "context": context,
            }
        )

    async def _save_performance_metrics(self):
        """Save performance metrics to file."""
        metrics = self.get_performance_summary()
        if not metrics:
            return

        # Create performance directory
        perf_dir = Path("test_performance")
        perf_dir.mkdir(exist_ok=True)

        # Save metrics with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.test_class_name}_{self.test_method_name}_{timestamp}.json"

        with open(perf_dir / filename, "w") as f:
            json.dump(
                {
                    "test_info": {
                        "class": self.test_class_name,
                        "method": self.test_method_name,
                        "timestamp": timestamp,
                    },
                    "metrics": metrics,
                },
                f,
                indent=2,
            )

    # Utility Methods for Common Test Patterns

    async def create_test_resource(
        self,
        resource_type: str,
        create_function: Callable,
        cleanup_function: Optional[Callable] = None,
        **create_kwargs,
    ) -> Any:
        """Create a test resource with automatic cleanup tracking.

        Args:
            resource_type: Type of resource being created
            create_function: Function to create the resource
            cleanup_function: Function to clean up the resource
            **create_kwargs: Arguments for the create function

        Returns:
            Created resource
        """
        # Generate unique name if not provided
        if "name" not in create_kwargs and "label" not in create_kwargs:
            if "label" in create_function.__code__.co_varnames:
                create_kwargs["label"] = self.generate_unique_label(resource_type)
            elif "name" in create_function.__code__.co_varnames:
                create_kwargs["name"] = self.generate_unique_name(resource_type)

        # Create the resource
        async with self.track_performance(f"create_{resource_type}"):
            await self.respect_rate_limits()

            if asyncio.iscoroutinefunction(create_function):
                resource = await create_function(**create_kwargs)
            else:
                resource = create_function(**create_kwargs)

        # Track for cleanup
        resource_id = getattr(resource, "id", getattr(resource, "label", str(resource)))
        self.track_resource(
            resource_type, resource_id, cleanup_function, **create_kwargs
        )

        return resource

    def assert_response_time_acceptable(
        self, operation_name: str, max_seconds: float = 5.0
    ):
        """Assert that a tracked operation completed within acceptable time."""
        self.assert_performance_within_limits(operation_name, max_seconds)

    # Integration with pytest fixtures

    @pytest.fixture(autouse=True)
    def _setup_base_test(self, request):
        """Auto-setup for base test functionality."""
        # This fixture is automatically used by all inheriting test classes
        self.request = request

        # Set rate limiting based on test environment
        if hasattr(request, "config"):
            if request.config.getoption("--live", default=False):
                self.set_rate_limit_delay(0.5)  # More conservative for live tests
            elif os.getenv("PYTEST_RATE_LIMITED", "").lower() in ("true", "1"):
                self.set_rate_limit_delay(0.2)  # Rate limited environment
            else:
                self.set_rate_limit_delay(0.0)  # No rate limiting for unit tests

        return self

    # Context managers for common patterns

    @asynccontextmanager
    async def api_call_context(
        self, endpoint_id: Optional[int] = None, operation_name: Optional[str] = None
    ):
        """Context manager for API calls with tracking and rate limiting.

        Args:
            endpoint_id: OFSC endpoint ID for context
            operation_name: Name for performance tracking
        """
        if endpoint_id:
            self.set_endpoint_context(endpoint_id)

        if operation_name:
            async with self.track_performance(operation_name):
                await self.respect_rate_limits()
                yield
        else:
            await self.respect_rate_limits()
            yield

    @asynccontextmanager
    async def expect_exception(
        self, exception_class: Type[Exception], message_contains: Optional[str] = None
    ):
        """Context manager for expecting specific exceptions.

        Args:
            exception_class: Expected exception class
            message_contains: Optional string that should be in exception message
        """
        try:
            yield
            # If we get here, no exception was raised
            raise AssertionError(
                f"Expected {exception_class.__name__} but no exception was raised"
            )
        except exception_class as e:
            if message_contains and message_contains not in str(e):
                raise AssertionError(
                    f"Exception message '{str(e)}' does not contain '{message_contains}'"
                ) from e
            # Expected exception was raised
            pass
        except Exception as e:
            raise AssertionError(
                f"Expected {exception_class.__name__} but got {type(e).__name__}: {e}"
            ) from e
