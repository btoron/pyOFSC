"""Async tests for property operations."""

import json
from pathlib import Path

import pytest

from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import Property, PropertyListResponse


class TestAsyncGetPropertiesLive:
    """Live tests against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_properties(self, async_instance):
        """Test get_properties with actual API - validates structure"""
        properties = await async_instance.metadata.get_properties(offset=0, limit=100)

        # Verify type validation
        assert isinstance(properties, PropertyListResponse)
        assert properties.totalResults is not None
        assert properties.totalResults >= 0
        assert hasattr(properties, "items")
        assert isinstance(properties.items, list)

        # Verify at least one property exists
        if len(properties.items) > 0:
            assert isinstance(properties.items[0], Property)


class TestAsyncGetProperties:
    """Test async get_properties method."""

    @pytest.mark.asyncio
    async def test_get_properties_with_model(self, async_instance):
        """Test that get_properties returns PropertyListResponse model"""
        properties = await async_instance.metadata.get_properties(offset=0, limit=100)

        # Verify type validation
        assert isinstance(properties, PropertyListResponse)
        assert hasattr(properties, "items")
        assert hasattr(properties, "totalResults")
        assert isinstance(properties.items, list)

        # Verify items are Property instances
        if len(properties.items) > 0:
            assert isinstance(properties.items[0], Property)
            assert hasattr(properties.items[0], "label")
            assert hasattr(properties.items[0], "name")
            assert hasattr(properties.items[0], "type")

    @pytest.mark.asyncio
    async def test_get_properties_pagination(self, async_instance):
        """Test get_properties with pagination"""
        # Get first page
        page1 = await async_instance.metadata.get_properties(offset=0, limit=5)
        assert isinstance(page1, PropertyListResponse)
        assert len(page1.items) <= 5

        # Get second page if there are enough properties
        if page1.totalResults > 5:
            page2 = await async_instance.metadata.get_properties(offset=5, limit=5)
            assert isinstance(page2, PropertyListResponse)
            # Pages should have different items
            if len(page1.items) > 0 and len(page2.items) > 0:
                assert page1.items[0].label != page2.items[0].label

    @pytest.mark.asyncio
    async def test_get_properties_total_results(self, async_instance):
        """Test that totalResults is populated"""
        properties = await async_instance.metadata.get_properties(offset=0, limit=100)
        assert properties.totalResults is not None
        assert isinstance(properties.totalResults, int)
        assert properties.totalResults >= 0


class TestAsyncGetProperty:
    """Test async get_property method."""

    @pytest.mark.asyncio
    async def test_get_property(self, async_instance):
        """Test getting a single property by label"""
        # First get a list of properties to get a valid label
        properties = await async_instance.metadata.get_properties(offset=0, limit=1)

        if len(properties.items) == 0:
            pytest.skip("No properties available to test")

        # Get the label of the first property
        label = properties.items[0].label

        # Get the specific property
        property_obj = await async_instance.metadata.get_property(label)

        # Verify type validation
        assert isinstance(property_obj, Property)
        assert property_obj.label == label
        assert hasattr(property_obj, "name")
        assert hasattr(property_obj, "type")

    @pytest.mark.asyncio
    async def test_get_property_details(self, async_instance):
        """Test that get_property returns complete property details"""
        # Get a known property
        properties = await async_instance.metadata.get_properties(offset=0, limit=1)

        if len(properties.items) == 0:
            pytest.skip("No properties available to test")

        label = properties.items[0].label

        # Get detailed property
        property_obj = await async_instance.metadata.get_property(label)

        # Verify all expected fields are present
        assert isinstance(property_obj, Property)
        assert property_obj.label == label
        assert property_obj.name is not None
        assert property_obj.type is not None

    @pytest.mark.asyncio
    async def test_get_property_not_found(self, async_instance):
        """Test that getting a non-existent property raises OFSCNotFoundError"""
        with pytest.raises(OFSCNotFoundError) as exc_info:
            await async_instance.metadata.get_property("NONEXISTENT_PROPERTY_12345")

        # Verify it's a 404 error
        assert exc_info.value.status_code == 404


class TestAsyncPropertySavedResponses:
    """Test model validation against saved API responses."""

    def test_property_list_response_validation(self):
        """Test PropertyListResponse model validates against saved response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "properties"
            / "get_properties_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        response = PropertyListResponse.model_validate(saved_data["response_data"])

        # Verify structure
        assert isinstance(response, PropertyListResponse)
        assert hasattr(response, "items")
        assert hasattr(response, "totalResults")
        assert len(response.items) > 0
        assert all(isinstance(item, Property) for item in response.items)

    def test_property_response_validation(self):
        """Test Property model validates against saved response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "properties"
            / "get_property_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        property_obj = Property.model_validate(saved_data["response_data"])

        # Verify structure
        assert isinstance(property_obj, Property)
        assert property_obj.label == "appt_number"
        assert property_obj.name == "Work Order"
        assert property_obj.type == "field"
        assert property_obj.entity is not None
        assert property_obj.gui == "text"
