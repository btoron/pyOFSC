"""Tests for async activities API methods."""

import json
from pathlib import Path

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import (
    Activity,
    ActivityCapacityCategoriesResponse,
    ActivityListResponse,
    InventoryListResponse,
    LinkedActivitiesResponse,
    RequiredInventoriesResponse,
    ResourcePreferencesResponse,
    SubmittedFormsResponse,
)


class TestAsyncGetActivitiesLive:
    """Live tests against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_activities(self, async_instance: AsyncOFSC):
        """Test get_activities with actual API - validates structure."""
        from calendar import monthrange
        from datetime import date

        # Calculate date range for current month (day 1 to last day)
        today = date.today()
        date_from = date(today.year, today.month, 1)
        last_day = monthrange(today.year, today.month)[1]
        date_to = date(today.year, today.month, last_day)

        result = await async_instance.core.get_activities(
            params={
                "dateFrom": date_from,
                "dateTo": date_to,
                "resources": ["SUNRISE"],
                "includeChildren": "all",
            },
            limit=100,
        )

        assert isinstance(result, ActivityListResponse)
        assert hasattr(result, "items")
        assert hasattr(result, "offset")
        assert hasattr(result, "limit")
        assert len(result.items) > 5, f"Expected more than 5 activities, got {len(result.items)}"
        assert len(result.items) <= 100


class TestAsyncGetActivities:
    """Model validation tests for get_activities."""

    @pytest.mark.asyncio
    async def test_get_activities_returns_model(self, async_instance: AsyncOFSC):
        """Test that get_activities returns ActivityListResponse model."""
        # This test will use the actual API
        # Skip if no credentials available
        pytest.skip("Requires API credentials and specific date range")

    @pytest.mark.asyncio
    async def test_get_activities_pagination(self, async_instance: AsyncOFSC):
        """Test get_activities with pagination parameters."""
        pytest.skip("Requires API credentials and specific date range")


class TestAsyncGetActivityLive:
    """Live tests for get_activity."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_activity(self, async_instance: AsyncOFSC):
        """Test get_activity with actual API."""
        activity_id = 3954799  # Known test activity
        result = await async_instance.core.get_activity(activity_id)

        assert isinstance(result, Activity)
        assert result.activityId == activity_id

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_activity_not_found(self, async_instance: AsyncOFSC):
        """Test get_activity with non-existent activity."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.core.get_activity(999999999)


class TestAsyncGetSubmittedFormsLive:
    """Live tests for get_submitted_forms."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_submitted_forms(self, async_instance: AsyncOFSC):
        """Test get_submitted_forms with actual API."""
        activity_id = 3954799
        result = await async_instance.core.get_submitted_forms(activity_id)

        assert isinstance(result, SubmittedFormsResponse)
        assert hasattr(result, "items")
        assert hasattr(result, "totalResults")
        assert hasattr(result, "hasMore")


class TestAsyncGetResourcePreferencesLive:
    """Live tests for get_resource_preferences."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resource_preferences(self, async_instance: AsyncOFSC):
        """Test get_resource_preferences with actual API."""
        activity_id = 3954799
        result = await async_instance.core.get_resource_preferences(activity_id)

        assert isinstance(result, ResourcePreferencesResponse)
        assert hasattr(result, "items")
        # Validate preference types if items exist
        for pref in result.items:
            assert pref.preferenceType in ["required", "preferred", "forbidden"]


class TestAsyncGetRequiredInventoriesLive:
    """Live tests for get_required_inventories."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_required_inventories(self, async_instance: AsyncOFSC):
        """Test get_required_inventories with actual API."""
        activity_id = 3954799
        result = await async_instance.core.get_required_inventories(activity_id)

        assert isinstance(result, RequiredInventoriesResponse)
        assert hasattr(result, "items")


class TestAsyncGetCustomerInventoriesLive:
    """Live tests for get_customer_inventories."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_customer_inventories(self, async_instance: AsyncOFSC):
        """Test get_customer_inventories with actual API."""
        activity_id = 3954799
        result = await async_instance.core.get_customer_inventories(activity_id)

        assert isinstance(result, InventoryListResponse)
        assert hasattr(result, "items")
        # Validate status field if items exist
        for inv in result.items:
            assert inv.status in [
                "customer",
                "resource",
                "installed",
                "deinstalled",
                None,
            ]


class TestAsyncGetInstalledInventoriesLive:
    """Live tests for get_installed_inventories."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_installed_inventories(self, async_instance: AsyncOFSC):
        """Test get_installed_inventories with actual API."""
        activity_id = 3954799
        result = await async_instance.core.get_installed_inventories(activity_id)

        assert isinstance(result, InventoryListResponse)
        assert hasattr(result, "items")


class TestAsyncGetDeinstalledInventoriesLive:
    """Live tests for get_deinstalled_inventories."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_deinstalled_inventories(self, async_instance: AsyncOFSC):
        """Test get_deinstalled_inventories with actual API."""
        activity_id = 3954799
        result = await async_instance.core.get_deinstalled_inventories(activity_id)

        assert isinstance(result, InventoryListResponse)
        assert hasattr(result, "items")


class TestAsyncGetLinkedActivitiesLive:
    """Live tests for get_linked_activities."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_linked_activities(self, async_instance: AsyncOFSC):
        """Test get_linked_activities with actual API."""
        activity_id = 3954799
        result = await async_instance.core.get_linked_activities(activity_id)

        assert isinstance(result, LinkedActivitiesResponse)
        assert hasattr(result, "items")
        # Validate link structure if items exist
        for link in result.items:
            assert hasattr(link, "fromActivityId")
            assert hasattr(link, "toActivityId")
            assert hasattr(link, "linkType")


class TestAsyncGetCapacityCategoriesLive:
    """Live tests for get_capacity_categories."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_categories(self, async_instance: AsyncOFSC):
        """Test get_capacity_categories with actual API."""
        activity_id = 3954799
        result = await async_instance.core.get_capacity_categories(activity_id)

        assert isinstance(result, ActivityCapacityCategoriesResponse)
        assert hasattr(result, "items")
        assert hasattr(result, "totalResults")


class TestAsyncActivitySavedResponses:
    """Saved response validation tests."""

    def test_activity_list_response_validation(self):
        """Test ActivityListResponse model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "activities"
            / "get_activities_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = ActivityListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, ActivityListResponse)
        assert hasattr(response, "items")
        assert len(response.items) > 0
        # Validate first activity has required fields
        first_activity = response.items[0]
        assert hasattr(first_activity, "activityId")

    def test_activity_single_response_validation(self):
        """Test Activity model validates against saved single response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "activities"
            / "get_activity_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        activity = Activity.model_validate(saved_data["response_data"])

        assert isinstance(activity, Activity)
        assert activity.activityId == 3954799

    def test_submitted_forms_response_validation(self):
        """Test SubmittedFormsResponse model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "activities"
            / "get_submitted_forms_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = SubmittedFormsResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, SubmittedFormsResponse)
        assert hasattr(response, "items")
        assert hasattr(response, "totalResults")
        assert hasattr(response, "hasMore")

    def test_resource_preferences_response_validation(self):
        """Test ResourcePreferencesResponse model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "activities"
            / "get_resource_preferences_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = ResourcePreferencesResponse.model_validate(
            saved_data["response_data"]
        )

        assert isinstance(response, ResourcePreferencesResponse)
        assert hasattr(response, "items")
        # Validate preference types
        for pref in response.items:
            assert pref.preferenceType in ["required", "preferred", "forbidden"]

    def test_required_inventories_response_validation(self):
        """Test RequiredInventoriesResponse model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "activities"
            / "get_required_inventories_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = RequiredInventoriesResponse.model_validate(
            saved_data["response_data"]
        )

        assert isinstance(response, RequiredInventoriesResponse)
        assert hasattr(response, "items")
        # Validate required inventory fields
        for inv in response.items:
            assert hasattr(inv, "inventoryType")
            assert hasattr(inv, "model")
            assert hasattr(inv, "quantity")

    def test_customer_inventories_response_validation(self):
        """Test InventoryListResponse model validates against customer inventories response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "activities"
            / "get_customer_inventories_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = InventoryListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, InventoryListResponse)
        assert hasattr(response, "items")
        # Validate inventory has expected fields
        for inv in response.items:
            assert inv.status == "customer" or inv.status is None
            assert hasattr(inv, "inventoryType")

    def test_installed_inventories_response_validation(self):
        """Test InventoryListResponse model validates against installed inventories response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "activities"
            / "get_installed_inventories_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = InventoryListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, InventoryListResponse)
        assert hasattr(response, "items")

    def test_deinstalled_inventories_response_validation(self):
        """Test InventoryListResponse model validates against deinstalled inventories response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "activities"
            / "get_deinstalled_inventories_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = InventoryListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, InventoryListResponse)
        assert hasattr(response, "items")

    def test_linked_activities_response_validation(self):
        """Test LinkedActivitiesResponse model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "activities"
            / "get_linked_activities_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = LinkedActivitiesResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, LinkedActivitiesResponse)
        assert hasattr(response, "items")
        # Validate link structure
        for link in response.items:
            assert hasattr(link, "fromActivityId")
            assert hasattr(link, "toActivityId")
            assert hasattr(link, "linkType")

    def test_capacity_categories_response_validation(self):
        """Test ActivityCapacityCategoriesResponse model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "activities"
            / "get_capacity_categories_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = ActivityCapacityCategoriesResponse.model_validate(
            saved_data["response_data"]
        )

        assert isinstance(response, ActivityCapacityCategoriesResponse)
        assert hasattr(response, "items")
        assert hasattr(response, "totalResults")
        # Validate capacity category structure
        for cat in response.items:
            assert hasattr(cat, "capacityCategory")
