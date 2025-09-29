# tests/utils/base_test.py
"""Base test class for Oracle Field Service API testing"""

import pytest
import json
import asyncio
from typing import Dict, Any, List, Type, TypeVar
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class APITestBase:
    """Base class for endpoint testing with common functionality"""

    # Override in subclasses
    ENDPOINT_NAME: str = None
    CLEANUP_ORDER: List[str] = [
        "reverse"
    ]  # or specific order like ["users", "activities", "resources"]

    @pytest.fixture(autouse=True)
    async def setup_test_tracking(self, request):
        """Track test execution details"""
        self.test_name = request.node.name
        self.start_time = datetime.now()
        yield
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()

    @pytest.fixture
    def error_reporter(self):
        """Error reporting utility"""
        reports = []

        def report_error(error: Exception, context: Dict[str, Any]):
            error_data = {
                "test_name": self.test_name,
                "endpoint": self.ENDPOINT_NAME,
                "timestamp": datetime.now().isoformat(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "duration": getattr(self, "duration", None),
            }

            # Add request/response details if available
            if hasattr(error, "request"):
                error_data["request"] = {
                    "method": error.request.method,
                    "url": str(error.request.url),
                    "headers": dict(error.request.headers),
                }

            if hasattr(error, "response"):
                error_data["response"] = {
                    "status_code": error.response.status_code,
                    "headers": dict(error.response.headers),
                    "body": error.response.text[:1000],  # First 1000 chars
                }

            reports.append(error_data)

            # Save to file
            error_dir = Path("error_reports") / self.ENDPOINT_NAME
            error_dir.mkdir(parents=True, exist_ok=True)

            filename = (
                f"{self.test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(error_dir / filename, "w") as f:
                json.dump(error_data, f, indent=2)

            return error_data

        yield report_error

        # Summary at the end
        if reports:
            print(f"\n⚠️  {len(reports)} errors reported for {self.ENDPOINT_NAME}")

    async def cleanup_resource(self, resource: Dict[str, Any], client):
        """Clean up a single resource - override in subclasses"""
        resource_type = resource.get("type")
        resource_id = resource.get("id")

        if not resource_type or not resource_id:
            return

        # Map resource types to cleanup methods
        cleanup_methods = {
            "activity": client.delete_activity,
            "resource": client.delete_resource,
            "user": client.delete_user,
            # Add more as needed
        }

        cleanup_method = cleanup_methods.get(resource_type)
        if cleanup_method:
            try:
                await cleanup_method(resource_id)
                print(f"✓ Cleaned up {resource_type}: {resource_id}")
            except Exception as e:
                print(f"✗ Failed to cleanup {resource_type} {resource_id}: {e}")

    @pytest.fixture
    async def auto_cleanup(self, created_resources, client, sandbox_config):
        """Automatic cleanup of created resources"""
        yield

        if not sandbox_config.get("cleanup_enabled", True):
            print("Cleanup disabled in configuration")
            return

        if not created_resources:
            return

        print(f"\n🧹 Cleaning up {len(created_resources)} resources...")

        # Group resources by type
        resources_by_type = {}
        for resource in created_resources:
            resource_type = resource.get("type")
            if resource_type not in resources_by_type:
                resources_by_type[resource_type] = []
            resources_by_type[resource_type].append(resource)

        # Clean up in specified order
        if self.CLEANUP_ORDER == ["reverse"]:
            # Clean up in reverse order of creation
            for resource in reversed(created_resources):
                await self.cleanup_resource(resource, client)
        else:
            # Clean up in specified type order
            for resource_type in self.CLEANUP_ORDER:
                if resource_type in resources_by_type:
                    for resource in resources_by_type[resource_type]:
                        await self.cleanup_resource(resource, client)

            # Clean up any remaining types
            for resource_type, resources in resources_by_type.items():
                if resource_type not in self.CLEANUP_ORDER:
                    for resource in resources:
                        await self.cleanup_resource(resource, client)

    async def assert_response_model(
        self, response: Any, model_class: Type[T], partial: bool = False
    ) -> T:
        """Validate response matches expected model"""
        assert response is not None, "Response should not be None"
        assert isinstance(response, model_class), (
            f"Expected {model_class.__name__}, got {type(response).__name__}"
        )

        # Additional validation
        if not partial:
            # Verify all required fields are present
            for field_name, field_info in model_class.model_fields.items():
                if field_info.is_required():
                    assert hasattr(response, field_name), (
                        f"Required field '{field_name}' missing in response"
                    )
                    assert getattr(response, field_name) is not None, (
                        f"Required field '{field_name}' is None"
                    )

        return response

    async def assert_error_response(
        self,
        error: Exception,
        expected_status: int,
        expected_message: str = None,
        expected_code: str = None,
    ):
        """Validate error response matches expectations"""
        if hasattr(error, "response"):
            assert error.response.status_code == expected_status, (
                f"Expected status {expected_status}, got {error.response.status_code}"
            )

        if expected_message:
            assert expected_message in str(error), (
                f"Expected message '{expected_message}' not found in error: {error}"
            )

        if expected_code and hasattr(error, "error_code"):
            assert error.error_code == expected_code, (
                f"Expected error code '{expected_code}', got '{error.error_code}'"
            )

    async def wait_for_eventual_consistency(
        self, check_func, timeout: int = 30, interval: int = 2
    ):
        """Wait for eventual consistency in the API"""
        start_time = datetime.now()

        while (datetime.now() - start_time).seconds < timeout:
            try:
                result = await check_func()
                if result:
                    return result
            except Exception:
                pass

            await asyncio.sleep(interval)

        raise TimeoutError(
            f"Eventual consistency not achieved within {timeout} seconds"
        )

    def generate_unique_name(self, prefix: str) -> str:
        """Generate unique name for test resources"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_test_{timestamp}_{self.test_name[:20]}"

    @pytest.fixture
    def track_performance(self):
        """Track API call performance"""
        metrics = []

        async def measure(func, *args, **kwargs):
            start = datetime.now()
            try:
                result = await func(*args, **kwargs)
                duration = (datetime.now() - start).total_seconds()
                metrics.append(
                    {"function": func.__name__, "duration": duration, "success": True}
                )
                return result
            except Exception as e:
                duration = (datetime.now() - start).total_seconds()
                metrics.append(
                    {
                        "function": func.__name__,
                        "duration": duration,
                        "success": False,
                        "error": str(e),
                    }
                )
                raise

        yield measure

        # Report metrics
        if metrics:
            avg_duration = sum(m["duration"] for m in metrics) / len(metrics)
            success_rate = sum(1 for m in metrics if m["success"]) / len(metrics) * 100
            print(
                f"\n📊 Performance: {len(metrics)} calls, "
                f"avg {avg_duration:.2f}s, "
                f"{success_rate:.0f}% success rate"
            )
