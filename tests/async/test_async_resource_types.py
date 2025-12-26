"""Async tests for resource type operations."""

import json
from pathlib import Path

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.models import ResourceType, ResourceTypeListResponse


class TestAsyncGetResourceTypesLive:
    """Live tests against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_types(self, async_instance: AsyncOFSC):
        """Test get_resource_types with actual API - validates structure"""
        resource_types = await async_instance.metadata.get_resource_types()

        # Verify type validation
        assert isinstance(resource_types, ResourceTypeListResponse)
        assert resource_types.totalResults is not None
        assert resource_types.totalResults >= 0
        assert hasattr(resource_types, "items")
        assert isinstance(resource_types.items, list)

        # Verify at least one resource type exists
        if len(resource_types.items) > 0:
            assert isinstance(resource_types.items[0], ResourceType)


class TestAsyncGetResourceTypes:
    """Test async get_resource_types method."""

    @pytest.mark.asyncio
    async def test_get_resource_types_with_model(self, async_instance: AsyncOFSC):
        """Test that get_resource_types returns ResourceTypeListResponse model"""
        resource_types = await async_instance.metadata.get_resource_types()

        # Verify type validation
        assert isinstance(resource_types, ResourceTypeListResponse)
        assert hasattr(resource_types, "items")
        assert hasattr(resource_types, "totalResults")
        assert isinstance(resource_types.items, list)

        # Verify items are ResourceType instances
        if len(resource_types.items) > 0:
            assert isinstance(resource_types.items[0], ResourceType)
            assert hasattr(resource_types.items[0], "label")
            assert hasattr(resource_types.items[0], "name")
            assert hasattr(resource_types.items[0], "active")

    @pytest.mark.asyncio
    async def test_get_resource_types_total_results(self, async_instance: AsyncOFSC):
        """Test that totalResults is populated"""
        resource_types = await async_instance.metadata.get_resource_types()
        assert resource_types.totalResults is not None
        assert isinstance(resource_types.totalResults, int)
        assert resource_types.totalResults >= 0

    @pytest.mark.asyncio
    async def test_get_resource_types_field_types(self, async_instance: AsyncOFSC):
        """Test that resource type fields have correct types"""
        resource_types = await async_instance.metadata.get_resource_types()

        if len(resource_types.items) > 0:
            resource_type = resource_types.items[0]
            assert isinstance(resource_type.label, str)
            assert isinstance(resource_type.name, str)
            assert isinstance(resource_type.active, bool)


class TestAsyncResourceTypeSavedResponses:
    """Test model validation against saved API responses."""

    def test_resource_type_list_response_validation(self):
        """Test ResourceTypeListResponse model validates against saved response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "resource_types"
            / "get_resource_types_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        response = ResourceTypeListResponse.model_validate(saved_data["response_data"])

        # Verify structure
        assert isinstance(response, ResourceTypeListResponse)
        assert hasattr(response, "items")
        assert hasattr(response, "totalResults")
        assert len(response.items) > 0
        assert all(isinstance(item, ResourceType) for item in response.items)

        # Verify first resource type details
        first_type = response.items[0]
        assert isinstance(first_type, ResourceType)
        assert first_type.label == "PR"
        assert first_type.name == "Technician"
        assert first_type.active is True
