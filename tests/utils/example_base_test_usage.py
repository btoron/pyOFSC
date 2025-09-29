"""
Example usage of BaseOFSCTest class.

This file demonstrates how to properly inherit from BaseOFSCTest and use its
features for comprehensive endpoint testing.
"""

import pytest

from ofsc.exceptions import OFSNotFoundException, OFSValidationException
from ofsc.models.metadata import PropertyResponse, PropertyListResponse
from tests.utils.base_test import BaseOFSCTest


class TestMetadataAPIExample(BaseOFSCTest):
    """Example test class demonstrating BaseOFSCTest usage."""

    @pytest.fixture(autouse=True)
    async def setup_client(self, async_client):
        """Setup OFSC client for tests."""
        self.client = async_client

    async def test_get_properties_with_performance_tracking(self):
        """Example: Test with performance tracking and validation."""

        # Set endpoint context for error reporting
        self.set_endpoint_context(endpoint_id=50)  # Properties endpoint

        # Track performance of the API call
        async with self.track_performance("get_properties"):
            async with self.api_call_context(operation_name="api_request"):
                response = await self.client.metadata.get_properties(limit=10)

        # Validate response model
        self.assert_pydantic_model_valid(response.dict(), PropertyListResponse)

        # Assert response structure
        response_data = response.dict()
        self.assert_response_structure(response_data)

        # Validate individual items
        properties = self.validate_list_response_models(
            response_data, PropertyResponse, min_items=1
        )

        # Assert performance is acceptable
        self.assert_response_time_acceptable("get_properties", max_seconds=3.0)

        # Add response context for debugging
        self.add_response_context(response_data, status_code=200)

    async def test_create_and_cleanup_test_property(self):
        """Example: Test with resource creation and automatic cleanup."""

        # Generate unique name for test property
        property_label = self.generate_unique_label("property")

        # Create test property data
        property_data = {
            "label": property_label,
            "name": f"Test Property {property_label}",
            "type": "string",
            "entity": "activity",
            "sharing": "private",
        }

        # Create the property with automatic cleanup tracking
        async def create_property():
            return await self.client.metadata.create_or_replace_property(
                property_label, property_data
            )

        async def cleanup_property():
            try:
                await self.client.metadata.delete_property(property_label)
            except OFSNotFoundException:
                pass  # Already deleted, that's fine

        # Create resource with tracking
        property_obj = await self.create_test_resource(
            resource_type="property",
            create_function=create_property,
            cleanup_function=cleanup_property,
        )

        # Validate created property
        self.assert_pydantic_model_valid(property_obj.dict(), PropertyResponse)
        assert property_obj.label == property_label
        assert property_obj.name == property_data["name"]

        # Test retrieval
        async with self.track_performance("get_created_property"):
            retrieved_property = await self.client.metadata.get_property(property_label)

        assert retrieved_property.label == property_label

        # Cleanup will happen automatically in teardown_method

    async def test_error_handling_with_context(self):
        """Example: Test error handling with detailed context."""

        self.set_endpoint_context(endpoint_id=51)  # Get property endpoint

        # Test with invalid property label
        invalid_label = "nonexistent_property_12345"

        # Use expect_exception context manager
        async with self.expect_exception(
            OFSNotFoundException, message_contains="not found"
        ):
            async with self.api_call_context(operation_name="get_invalid_property"):
                await self.client.metadata.get_property(invalid_label)

    async def test_validation_error_handling(self):
        """Example: Test validation error handling."""

        # Test with invalid parameters
        with pytest.raises(OFSValidationException) as exc_info:
            await self.client.metadata.get_properties(limit=-1)  # Invalid limit

        # Validate error details
        error = exc_info.value
        assert "limit" in str(error).lower()
        assert "negative" in str(error).lower() or "invalid" in str(error).lower()

    async def test_rate_limiting_behavior(self):
        """Example: Test with custom rate limiting."""

        # Set custom rate limit for this test
        self.set_rate_limit_delay(0.5)  # 500ms between requests

        # Make multiple requests and measure timing
        async with self.track_performance("rate_limited_requests"):
            for i in range(3):
                async with self.api_call_context(operation_name=f"request_{i}"):
                    await self.client.metadata.get_properties(limit=1, offset=i)

        # Check that rate limiting was applied
        metrics = self.get_performance_summary()
        total_time = metrics["rate_limited_requests"]["total"]

        # Should take at least 1 second (2 delays of 0.5s each between 3 requests)
        assert total_time >= 1.0, f"Rate limiting not applied correctly: {total_time}s"

    async def test_bulk_operations_with_tracking(self):
        """Example: Test bulk operations with resource tracking."""

        # Create multiple test properties
        property_labels = []

        for i in range(3):
            label = self.generate_unique_label("bulk_prop")
            property_labels.append(label)

            # Track each property for cleanup
            async def cleanup_func(lbl=label):  # Capture label in closure
                try:
                    await self.client.metadata.delete_property(lbl)
                except OFSNotFoundException:
                    pass

            self.track_resource("property", label, cleanup_func)

        # Create properties with performance tracking
        created_properties = []
        async with self.track_performance("bulk_create_properties"):
            for label in property_labels:
                property_data = {
                    "label": label,
                    "name": f"Bulk Test Property {label}",
                    "type": "string",
                    "entity": "activity",
                    "sharing": "private",
                }

                async with self.api_call_context():
                    prop = await self.client.metadata.create_or_replace_property(
                        label, property_data
                    )
                    created_properties.append(prop)

        # Validate all were created
        assert len(created_properties) == 3
        for prop in created_properties:
            self.assert_pydantic_model_valid(prop.dict(), PropertyResponse)

        # Verify we can retrieve them
        async with self.track_performance("bulk_retrieve_properties"):
            for label in property_labels:
                async with self.api_call_context():
                    retrieved = await self.client.metadata.get_property(label)
                    assert retrieved.label == label

        # Check performance metrics
        create_metrics = self.get_performance_summary()["bulk_create_properties"]
        retrieve_metrics = self.get_performance_summary()["bulk_retrieve_properties"]

        # Assert reasonable performance (adjust thresholds as needed)
        assert create_metrics["average"] < 2.0, "Property creation too slow"
        assert retrieve_metrics["average"] < 1.0, "Property retrieval too slow"

        # All properties will be cleaned up automatically via tracked cleanup functions


# Additional example showing integration with pytest fixtures
class TestAdvancedUsageExample(BaseOFSCTest):
    """Advanced usage examples."""

    @pytest.fixture(autouse=True)
    async def setup_test_data(self, async_client):
        """Setup test data with automatic cleanup."""
        self.client = async_client

        # Create a test workskill that will be used across multiple tests
        self.test_workskill_label = self.generate_unique_label("workskill")

        workskill_data = {
            "label": self.test_workskill_label,
            "name": f"Test Workskill {self.test_workskill_label}",
            "sharing": "maximal",
        }

        # Create and track the workskill
        async def cleanup_workskill():
            try:
                await self.client.metadata.delete_workskill(self.test_workskill_label)
            except OFSNotFoundException:
                pass

        self.test_workskill = await self.create_test_resource(
            resource_type="workskill",
            create_function=lambda: self.client.metadata.create_or_replace_workskill(
                self.test_workskill_label, workskill_data
            ),
            cleanup_function=cleanup_workskill,
        )

    async def test_using_shared_test_data(self):
        """Test that uses the shared test workskill."""

        # Use the workskill created in setup
        async with self.track_performance("get_shared_workskill"):
            retrieved = await self.client.metadata.get_workskill(
                self.test_workskill_label
            )

        assert retrieved.label == self.test_workskill_label
        assert retrieved.name == self.test_workskill.name

        # Modify the workskill
        updated_data = retrieved.dict()
        updated_data["name"] = f"Updated {retrieved.name}"

        async with self.track_performance("update_shared_workskill"):
            updated = await self.client.metadata.create_or_replace_workskill(
                self.test_workskill_label, updated_data
            )

        assert updated.name == updated_data["name"]

    async def test_complex_validation_scenario(self):
        """Test complex validation with multiple models."""

        # Get a list of workskills
        async with self.track_performance("get_workskills_list"):
            workskills_response = await self.client.metadata.get_workskills(limit=5)

        # Validate the list response structure
        response_data = workskills_response.dict()
        self.assert_response_structure(response_data)

        # Validate each workskill in the response
        workskills = response_data.get("items", [])
        assert len(workskills) > 0, "No workskills found in response"

        for workskill_data in workskills:
            # Validate each workskill structure
            self.assert_pydantic_model_valid(workskill_data, type(self.test_workskill))

            # Verify required fields
            assert "label" in workskill_data
            assert "name" in workskill_data
            assert "sharing" in workskill_data

            # Validate field constraints
            assert len(workskill_data["label"]) <= 40, "Label too long"
            assert workskill_data["sharing"] in ["private", "maximal", "no sharing"]
