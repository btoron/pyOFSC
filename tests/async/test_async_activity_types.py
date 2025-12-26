"""Async tests for activity type operations."""

import json
from pathlib import Path

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import ActivityType, ActivityTypeListResponse


class TestAsyncGetActivityTypesLive:
    """Live tests against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_activity_types(self, async_instance: AsyncOFSC):
        """Test get_activity_types with actual API - validates structure"""
        activity_types = await async_instance.metadata.get_activity_types(
            offset=0, limit=100
        )

        # Verify type validation
        assert isinstance(activity_types, ActivityTypeListResponse)
        assert activity_types.totalResults is not None
        assert activity_types.totalResults >= 0
        assert hasattr(activity_types, "items")
        assert isinstance(activity_types.items, list)

        # Verify at least one activity type exists
        if len(activity_types.items) > 0:
            assert isinstance(activity_types.items[0], ActivityType)


class TestAsyncGetActivityTypes:
    """Test async get_activity_types method."""

    @pytest.mark.asyncio
    async def test_get_activity_types_with_model(self, async_instance: AsyncOFSC):
        """Test that get_activity_types returns ActivityTypeListResponse model"""
        activity_types = await async_instance.metadata.get_activity_types(
            offset=0, limit=100
        )

        # Verify type validation
        assert isinstance(activity_types, ActivityTypeListResponse)
        assert hasattr(activity_types, "items")
        assert hasattr(activity_types, "totalResults")
        assert isinstance(activity_types.items, list)

        # Verify items are ActivityType instances
        if len(activity_types.items) > 0:
            assert isinstance(activity_types.items[0], ActivityType)
            assert hasattr(activity_types.items[0], "label")
            assert hasattr(activity_types.items[0], "name")
            assert hasattr(activity_types.items[0], "active")

    @pytest.mark.asyncio
    async def test_get_activity_types_pagination(self, async_instance: AsyncOFSC):
        """Test get_activity_types with pagination"""
        # Get first page
        page1 = await async_instance.metadata.get_activity_types(offset=0, limit=3)
        assert isinstance(page1, ActivityTypeListResponse)
        assert len(page1.items) <= 3

        # Get second page if there are enough activity types
        if page1.totalResults > 3:
            page2 = await async_instance.metadata.get_activity_types(offset=3, limit=3)
            assert isinstance(page2, ActivityTypeListResponse)
            # Pages should have different items
            if len(page1.items) > 0 and len(page2.items) > 0:
                assert page1.items[0].label != page2.items[0].label

    @pytest.mark.asyncio
    async def test_get_activity_types_total_results(self, async_instance: AsyncOFSC):
        """Test that totalResults is populated"""
        activity_types = await async_instance.metadata.get_activity_types(
            offset=0, limit=100
        )
        assert activity_types.totalResults is not None
        assert isinstance(activity_types.totalResults, int)
        assert activity_types.totalResults >= 0

    @pytest.mark.asyncio
    async def test_get_activity_types_field_types(self, async_instance: AsyncOFSC):
        """Test that activity type fields have correct types"""
        activity_types = await async_instance.metadata.get_activity_types(
            offset=0, limit=100
        )

        if len(activity_types.items) > 0:
            activity_type = activity_types.items[0]
            assert isinstance(activity_type.label, str)
            assert isinstance(activity_type.name, str)
            assert isinstance(activity_type.active, bool)


class TestAsyncGetActivityType:
    """Test async get_activity_type method."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_activity_type(self, async_instance: AsyncOFSC):
        """Test get_activity_type with actual API"""
        # Use "LU" label from saved response
        activity_type = await async_instance.metadata.get_activity_type("LU")

        # Verify type validation
        assert isinstance(activity_type, ActivityType)
        assert activity_type.label == "LU"
        assert isinstance(activity_type.name, str)
        assert isinstance(activity_type.active, bool)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_activity_type_not_found(self, async_instance: AsyncOFSC):
        """Test get_activity_type with non-existent type"""
        with pytest.raises(OFSCNotFoundError) as exc_info:
            await async_instance.metadata.get_activity_type("NONEXISTENT_TYPE_12345")

        # Verify error details
        assert exc_info.value.status_code == 404


class TestAsyncActivityTypeSavedResponses:
    """Test model validation against saved API responses."""

    def test_activity_type_list_response_validation(self):
        """Test ActivityTypeListResponse model validates against saved response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "activity_types"
            / "get_activity_types_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        response = ActivityTypeListResponse.model_validate(saved_data["response_data"])

        # Verify structure
        assert isinstance(response, ActivityTypeListResponse)
        assert hasattr(response, "items")
        assert hasattr(response, "totalResults")
        assert len(response.items) > 0
        assert all(isinstance(item, ActivityType) for item in response.items)

        # Verify first activity type details
        first_type = response.items[0]
        assert isinstance(first_type, ActivityType)
        assert isinstance(first_type.label, str)
        assert isinstance(first_type.name, str)
        assert isinstance(first_type.active, bool)

    def test_activity_type_single_response_validation(self):
        """Test ActivityType model validates against saved single response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "activity_types"
            / "get_activity_type_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        activity_type = ActivityType.model_validate(saved_data["response_data"])

        # Verify structure
        assert isinstance(activity_type, ActivityType)
        assert activity_type.label == "LU"
        assert isinstance(activity_type.name, str)
        assert isinstance(activity_type.active, bool)
