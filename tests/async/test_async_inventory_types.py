"""Async tests for inventory type operations."""

import json
from pathlib import Path

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import InventoryType, InventoryTypeListResponse, TranslationList


class TestAsyncGetInventoryTypesLive:
    """Live tests against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_inventory_types(self, async_instance: AsyncOFSC):
        """Test get_inventory_types with actual API - validates structure"""
        inventory_types = await async_instance.metadata.get_inventory_types()

        # Verify type validation
        assert isinstance(inventory_types, InventoryTypeListResponse)
        assert inventory_types.totalResults is not None
        assert inventory_types.totalResults >= 0
        assert hasattr(inventory_types, "items")
        assert isinstance(inventory_types.items, list)

        # Verify at least one inventory type exists
        if len(inventory_types.items) > 0:
            assert isinstance(inventory_types.items[0], InventoryType)


class TestAsyncGetInventoryTypes:
    """Test async get_inventory_types method."""

    @pytest.mark.asyncio
    async def test_get_inventory_types_with_model(self, async_instance: AsyncOFSC):
        """Test that get_inventory_types returns InventoryTypeListResponse model"""
        inventory_types = await async_instance.metadata.get_inventory_types()

        # Verify type validation
        assert isinstance(inventory_types, InventoryTypeListResponse)
        assert hasattr(inventory_types, "items")
        assert hasattr(inventory_types, "totalResults")
        assert isinstance(inventory_types.items, list)

        # Verify items are InventoryType instances
        if len(inventory_types.items) > 0:
            assert isinstance(inventory_types.items[0], InventoryType)
            assert hasattr(inventory_types.items[0], "label")
            assert hasattr(inventory_types.items[0], "active")
            assert hasattr(inventory_types.items[0], "translations")

    @pytest.mark.asyncio
    async def test_get_inventory_types_pagination(self, async_instance: AsyncOFSC):
        """Test get_inventory_types with pagination"""
        inventory_types = await async_instance.metadata.get_inventory_types(
            offset=0, limit=2
        )
        assert isinstance(inventory_types, InventoryTypeListResponse)
        assert inventory_types.totalResults is not None

    @pytest.mark.asyncio
    async def test_get_inventory_types_total_results(self, async_instance: AsyncOFSC):
        """Test that totalResults is populated"""
        inventory_types = await async_instance.metadata.get_inventory_types()
        assert inventory_types.totalResults is not None
        assert isinstance(inventory_types.totalResults, int)
        assert inventory_types.totalResults >= 0

    @pytest.mark.asyncio
    async def test_get_inventory_types_field_types(self, async_instance: AsyncOFSC):
        """Test that inventory type fields have correct types"""
        inventory_types = await async_instance.metadata.get_inventory_types()

        if len(inventory_types.items) > 0:
            inventory_type = inventory_types.items[0]
            assert isinstance(inventory_type.label, str)
            assert isinstance(inventory_type.active, bool)
            # translations can be None or TranslationList
            if inventory_type.translations is not None:
                assert isinstance(inventory_type.translations, TranslationList)


class TestAsyncGetInventoryType:
    """Test async get_inventory_type method."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_inventory_type(self, async_instance: AsyncOFSC):
        """Test get_inventory_type with actual API"""
        # Get list of inventory types first to find a valid one
        inventory_types = await async_instance.metadata.get_inventory_types()
        assert len(inventory_types.items) > 0

        # Get the first inventory type by label
        first_label = inventory_types.items[0].label
        inventory_type = await async_instance.metadata.get_inventory_type(first_label)

        # Verify type validation
        assert isinstance(inventory_type, InventoryType)
        assert inventory_type.label == first_label
        assert isinstance(inventory_type.active, bool)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_inventory_type_not_found(self, async_instance: AsyncOFSC):
        """Test get_inventory_type with non-existent inventory type"""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_inventory_type("NONEXISTENT_TYPE_12345")


class TestAsyncInventoryTypeSavedResponses:
    """Test model validation against saved API responses."""

    def test_inventory_type_list_response_validation(self):
        """Test InventoryTypeListResponse model validates against saved response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "inventory_types"
            / "get_inventory_types_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        response = InventoryTypeListResponse.model_validate(saved_data["response_data"])

        # Verify structure
        assert isinstance(response, InventoryTypeListResponse)
        assert hasattr(response, "items")
        assert hasattr(response, "totalResults")
        assert len(response.items) > 0
        assert all(isinstance(item, InventoryType) for item in response.items)

        # Verify first inventory type details
        first_type = response.items[0]
        assert isinstance(first_type, InventoryType)
        assert first_type.label == "gend205"
        assert first_type.active is True

    def test_inventory_type_single_response_validation(self):
        """Test InventoryType model validates against saved single response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "inventory_types"
            / "get_inventory_type_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        inventory_type = InventoryType.model_validate(saved_data["response_data"])

        # Verify structure
        assert isinstance(inventory_type, InventoryType)
        assert inventory_type.label == "gend205"
        assert inventory_type.active is True
