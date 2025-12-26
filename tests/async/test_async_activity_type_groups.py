"""Async tests for activity type group operations."""

import json
from pathlib import Path

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import ActivityTypeGroup, ActivityTypeGroupListResponse


class TestAsyncGetActivityTypeGroupsLive:
    """Live tests against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_activity_type_groups(self, async_instance: AsyncOFSC):
        """Test get_activity_type_groups with actual API - validates structure"""
        activity_type_groups = await async_instance.metadata.get_activity_type_groups(
            offset=0, limit=100
        )

        # Verify type validation
        assert isinstance(activity_type_groups, ActivityTypeGroupListResponse)
        assert activity_type_groups.totalResults is not None
        assert activity_type_groups.totalResults >= 0
        assert hasattr(activity_type_groups, "items")
        assert isinstance(activity_type_groups.items, list)

        # Verify at least one activity type group exists
        if len(activity_type_groups.items) > 0:
            assert isinstance(activity_type_groups.items[0], ActivityTypeGroup)


class TestAsyncGetActivityTypeGroups:
    """Test async get_activity_type_groups method."""

    @pytest.mark.asyncio
    async def test_get_activity_type_groups_with_model(self, async_instance: AsyncOFSC):
        """Test that get_activity_type_groups returns ActivityTypeGroupListResponse model"""
        activity_type_groups = await async_instance.metadata.get_activity_type_groups(
            offset=0, limit=100
        )

        # Verify type validation
        assert isinstance(activity_type_groups, ActivityTypeGroupListResponse)
        assert hasattr(activity_type_groups, "items")
        assert hasattr(activity_type_groups, "totalResults")
        assert isinstance(activity_type_groups.items, list)

        # Verify items are ActivityTypeGroup instances
        if len(activity_type_groups.items) > 0:
            assert isinstance(activity_type_groups.items[0], ActivityTypeGroup)
            assert hasattr(activity_type_groups.items[0], "label")
            assert hasattr(activity_type_groups.items[0], "name")

    @pytest.mark.asyncio
    async def test_get_activity_type_groups_pagination(self, async_instance: AsyncOFSC):
        """Test get_activity_type_groups with pagination"""
        # Get first page
        page1 = await async_instance.metadata.get_activity_type_groups(
            offset=0, limit=3
        )
        assert isinstance(page1, ActivityTypeGroupListResponse)
        assert len(page1.items) <= 3

        # Get second page if there are enough activity type groups
        if page1.totalResults > 3:
            page2 = await async_instance.metadata.get_activity_type_groups(
                offset=3, limit=3
            )
            assert isinstance(page2, ActivityTypeGroupListResponse)
            # Pages should have different items
            if len(page1.items) > 0 and len(page2.items) > 0:
                assert page1.items[0].label != page2.items[0].label

    @pytest.mark.asyncio
    async def test_get_activity_type_groups_total_results(
        self, async_instance: AsyncOFSC
    ):
        """Test that totalResults is populated"""
        activity_type_groups = await async_instance.metadata.get_activity_type_groups(
            offset=0, limit=100
        )
        assert activity_type_groups.totalResults is not None
        assert isinstance(activity_type_groups.totalResults, int)
        assert activity_type_groups.totalResults >= 0

    @pytest.mark.asyncio
    async def test_get_activity_type_groups_field_types(
        self, async_instance: AsyncOFSC
    ):
        """Test that activity type group fields have correct types"""
        activity_type_groups = await async_instance.metadata.get_activity_type_groups(
            offset=0, limit=100
        )

        if len(activity_type_groups.items) > 0:
            group = activity_type_groups.items[0]
            assert isinstance(group.label, str)
            assert isinstance(group.name, str)


class TestAsyncGetActivityTypeGroup:
    """Test async get_activity_type_group method."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_activity_type_group(self, async_instance: AsyncOFSC):
        """Test get_activity_type_group with actual API"""
        # Use "customer" label from existing tests
        group = await async_instance.metadata.get_activity_type_group("customer")

        # Verify type validation
        assert isinstance(group, ActivityTypeGroup)
        assert group.label == "customer"
        assert isinstance(group.name, str)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_activity_type_group_not_found(self, async_instance: AsyncOFSC):
        """Test get_activity_type_group with non-existent group"""
        with pytest.raises(OFSCNotFoundError) as exc_info:
            await async_instance.metadata.get_activity_type_group(
                "NONEXISTENT_GROUP_12345"
            )

        # Verify error details
        assert exc_info.value.status_code == 404


class TestAsyncActivityTypeGroupSavedResponses:
    """Test model validation against saved API responses."""

    def test_activity_type_group_list_response_validation(self):
        """Test ActivityTypeGroupListResponse model validates against saved response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "activity_type_groups"
            / "get_activity_type_groups_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        response = ActivityTypeGroupListResponse.model_validate(
            saved_data["response_data"]
        )

        # Verify structure
        assert isinstance(response, ActivityTypeGroupListResponse)
        assert hasattr(response, "items")
        assert hasattr(response, "totalResults")
        assert len(response.items) > 0
        assert all(isinstance(item, ActivityTypeGroup) for item in response.items)

        # Verify first activity type group details
        first_group = response.items[0]
        assert isinstance(first_group, ActivityTypeGroup)
        assert isinstance(first_group.label, str)
        assert isinstance(first_group.name, str)

    def test_activity_type_group_single_response_validation(self):
        """Test ActivityTypeGroup model validates against saved single response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "activity_type_groups"
            / "get_activity_type_group_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        group = ActivityTypeGroup.model_validate(saved_data["response_data"])

        # Verify structure
        assert isinstance(group, ActivityTypeGroup)
        assert group.label == "customer"
        assert isinstance(group.name, str)
