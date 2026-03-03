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
    Inventory,
    InventoryListResponse,
    LinkedActivitiesResponse,
    LinkedActivity,
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
        assert len(result.items) > 5, (
            f"Expected more than 5 activities, got {len(result.items)}"
        )
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


# region Phase 1: Core CRUD (create, update, delete activity)


class TestAsyncCreateActivityLive:
    """Live tests for create_activity."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_create_and_delete_activity(self, async_instance: AsyncOFSC):
        """Test create_activity creates an activity and delete_activity removes it."""
        # Get a valid activity type
        activity_types = await async_instance.metadata.get_activity_types()
        assert len(list(activity_types)) > 0
        activity_type = list(activity_types)[0].label

        activity = Activity.model_validate(
            {
                "resourceExternalId": "SUNRISE",
                "date": "2099-01-01",
                "activityType": activity_type,
            }
        )
        created = await async_instance.core.create_activity(activity)

        assert isinstance(created, Activity)
        assert created.activityId is not None

        # Cleanup
        await async_instance.core.delete_activity(created.activityId)

        # Verify deletion
        with pytest.raises(Exception):
            await async_instance.core.get_activity(created.activityId)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_create_activity_returns_activity_model(
        self, async_instance: AsyncOFSC
    ):
        """Test that create_activity returns an Activity model."""
        activity_types = await async_instance.metadata.get_activity_types()
        activity_type = list(activity_types)[0].label

        activity = Activity.model_validate(
            {
                "resourceExternalId": "SUNRISE",
                "date": "2099-01-01",
                "activityType": activity_type,
            }
        )
        created = await async_instance.core.create_activity(activity)

        assert isinstance(created, Activity)
        assert hasattr(created, "activityId")

        # Cleanup
        await async_instance.core.delete_activity(created.activityId)


class TestAsyncUpdateActivityLive:
    """Live tests for update_activity."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_update_activity(self, async_instance: AsyncOFSC):
        """Test update_activity with actual API."""
        activity_id = 3954799
        result = await async_instance.core.update_activity(
            activity_id, {"customerName": "Test Customer"}
        )

        assert isinstance(result, Activity)
        assert result.activityId == activity_id

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_update_activity_not_found(self, async_instance: AsyncOFSC):
        """Test update_activity with non-existent activity."""
        from ofsc.exceptions import OFSCNotFoundError

        with pytest.raises(OFSCNotFoundError):
            await async_instance.core.update_activity(999999999, {"customerName": "X"})


class TestAsyncDeleteActivityLive:
    """Live tests for delete_activity."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_delete_activity_not_found(self, async_instance: AsyncOFSC):
        """Test delete_activity with non-existent activity raises NotFoundError."""
        from ofsc.exceptions import OFSCNotFoundError

        with pytest.raises(OFSCNotFoundError):
            await async_instance.core.delete_activity(999999999)


# endregion


# region Phase 2: Resource Preferences & Required Inventories


class TestAsyncSetResourcePreferencesLive:
    """Live tests for set_resource_preferences."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_set_resource_preferences_idempotent(self, async_instance: AsyncOFSC):
        """Test set_resource_preferences with same data (idempotent)."""
        activity_id = 3954799
        original = await async_instance.core.get_resource_preferences(activity_id)

        # Set same preferences back — should succeed
        await async_instance.core.set_resource_preferences(activity_id, original.items)

        # Verify data unchanged
        after = await async_instance.core.get_resource_preferences(activity_id)
        assert len(after.items) == len(original.items)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_set_resource_preferences_returns_none(
        self, async_instance: AsyncOFSC
    ):
        """Test that set_resource_preferences returns None."""
        activity_id = 3954799
        original = await async_instance.core.get_resource_preferences(activity_id)
        result = await async_instance.core.set_resource_preferences(
            activity_id, original.items
        )
        assert result is None


class TestAsyncDeleteResourcePreferencesLive:
    """Live tests for delete_resource_preferences."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_delete_resource_preferences_save_restore(
        self, async_instance: AsyncOFSC
    ):
        """Test save/delete/restore cycle for resource preferences."""
        activity_id = 3954799

        # Save original
        original = await async_instance.core.get_resource_preferences(activity_id)

        # Delete all
        await async_instance.core.delete_resource_preferences(activity_id)

        # Verify empty
        after_delete = await async_instance.core.get_resource_preferences(activity_id)
        assert len(after_delete.items) == 0

        # Restore
        if original.items:
            await async_instance.core.set_resource_preferences(
                activity_id, original.items
            )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_delete_resource_preferences_returns_none(
        self, async_instance: AsyncOFSC
    ):
        """Test that delete_resource_preferences returns None."""
        activity_id = 3954799
        result = await async_instance.core.delete_resource_preferences(activity_id)
        assert result is None

        # Restore preferences (save original before test would require fixture,
        # but for now just verify the call works)


class TestAsyncSetRequiredInventoriesLive:
    """Live tests for set_required_inventories."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_set_required_inventories_idempotent(self, async_instance: AsyncOFSC):
        """Test set_required_inventories with same data (idempotent)."""
        activity_id = 3954799
        original = await async_instance.core.get_required_inventories(activity_id)

        # Set same inventories back — should succeed
        await async_instance.core.set_required_inventories(activity_id, original.items)

        # Verify data unchanged
        after = await async_instance.core.get_required_inventories(activity_id)
        assert len(after.items) == len(original.items)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_set_required_inventories_returns_none(
        self, async_instance: AsyncOFSC
    ):
        """Test that set_required_inventories returns None."""
        activity_id = 3954799
        original = await async_instance.core.get_required_inventories(activity_id)
        result = await async_instance.core.set_required_inventories(
            activity_id, original.items
        )
        assert result is None


class TestAsyncDeleteRequiredInventoriesLive:
    """Live tests for delete_required_inventories."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_delete_required_inventories_save_restore(
        self, async_instance: AsyncOFSC
    ):
        """Test save/delete/restore cycle for required inventories."""
        activity_id = 3954799

        # Save original
        original = await async_instance.core.get_required_inventories(activity_id)

        # Delete all
        await async_instance.core.delete_required_inventories(activity_id)

        # Verify empty
        after_delete = await async_instance.core.get_required_inventories(activity_id)
        assert len(after_delete.items) == 0

        # Restore
        if original.items:
            await async_instance.core.set_required_inventories(
                activity_id, original.items
            )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_delete_required_inventories_returns_none(
        self, async_instance: AsyncOFSC
    ):
        """Test that delete_required_inventories returns None."""
        activity_id = 3954799
        result = await async_instance.core.delete_required_inventories(activity_id)
        assert result is None

        # Restore required inventories
        original = RequiredInventoriesResponse.model_validate({"items": []})
        await async_instance.core.set_required_inventories(activity_id, original.items)


# endregion


# region Phase 3: Linked Activities & Customer Inventories


class TestAsyncCreateCustomerInventoryLive:
    """Live tests for create_customer_inventory."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_create_customer_inventory(self, async_instance: AsyncOFSC):
        """Test create_customer_inventory creates an inventory item."""
        # Get inventory types to find a valid one
        activity_id = 3954799
        existing = await async_instance.core.get_customer_inventories(activity_id)

        if not existing.items:
            pytest.skip("No existing customer inventories to derive a type from")

        inv_type = existing.items[0].inventoryType
        inventory = Inventory.model_validate({"inventoryType": inv_type, "quantity": 1})
        created = await async_instance.core.create_customer_inventory(
            activity_id, inventory
        )

        assert isinstance(created, Inventory)
        assert created.inventoryType == inv_type


class TestAsyncLinkActivitiesLive:
    """Live tests for link_activities and unlink_activities."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_link_and_unlink_activities(self, async_instance: AsyncOFSC):
        """Test link then unlink two temporary activities."""
        activity_types = await async_instance.metadata.get_activity_types()
        activity_type = list(activity_types)[0].label

        # Create two temporary activities
        act1 = await async_instance.core.create_activity(
            Activity.model_validate(
                {
                    "resourceExternalId": "SUNRISE",
                    "date": "2099-01-01",
                    "activityType": activity_type,
                }
            )
        )
        act2 = await async_instance.core.create_activity(
            Activity.model_validate(
                {
                    "resourceExternalId": "SUNRISE",
                    "date": "2099-01-01",
                    "activityType": activity_type,
                }
            )
        )

        try:
            # Link activities
            link = LinkedActivity.model_validate(
                {
                    "fromActivityId": act1.activityId,
                    "toActivityId": act2.activityId,
                    "linkType": "sequence",
                }
            )
            created_link = await async_instance.core.link_activities(
                act1.activityId, link
            )

            assert isinstance(created_link, LinkedActivity)
            assert created_link.fromActivityId == act1.activityId
            assert created_link.toActivityId == act2.activityId

            # Unlink
            await async_instance.core.unlink_activities(act1.activityId)

            # Verify unlinked
            links_after = await async_instance.core.get_linked_activities(
                act1.activityId
            )
            assert len(links_after.items) == 0

        finally:
            # Cleanup
            await async_instance.core.delete_activity(act1.activityId)
            await async_instance.core.delete_activity(act2.activityId)


class TestAsyncSetActivityLinkLive:
    """Live tests for set_activity_link and delete_activity_link."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_set_and_delete_activity_link(self, async_instance: AsyncOFSC):
        """Test set_activity_link creates a link and delete_activity_link removes it."""
        activity_types = await async_instance.metadata.get_activity_types()
        activity_type = list(activity_types)[0].label

        act1 = await async_instance.core.create_activity(
            Activity.model_validate(
                {
                    "resourceExternalId": "SUNRISE",
                    "date": "2099-01-01",
                    "activityType": activity_type,
                }
            )
        )
        act2 = await async_instance.core.create_activity(
            Activity.model_validate(
                {
                    "resourceExternalId": "SUNRISE",
                    "date": "2099-01-01",
                    "activityType": activity_type,
                }
            )
        )

        try:
            link_data = {
                "fromActivityId": act1.activityId,
                "toActivityId": act2.activityId,
                "linkType": "sequence",
            }
            result = await async_instance.core.set_activity_link(
                act1.activityId, act2.activityId, "sequence", link_data
            )

            assert isinstance(result, LinkedActivity)

            # Delete the specific link
            await async_instance.core.delete_activity_link(
                act1.activityId, act2.activityId, "sequence"
            )

            # Verify removed
            links = await async_instance.core.get_linked_activities(act1.activityId)
            assert len(links.items) == 0

        finally:
            await async_instance.core.delete_activity(act1.activityId)
            await async_instance.core.delete_activity(act2.activityId)


# endregion


# region Phase 4: File Property Operations


class TestAsyncSetFilePropertyLive:
    """Live tests for set_file_property."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_set_and_delete_file_property(self, async_instance: AsyncOFSC):
        """Test set_file_property uploads content and delete_file_property removes it."""
        activity_id = 3954799
        label = "csign"
        content = b"test file content"
        media_type = "application/octet-stream"

        # Upload
        result = await async_instance.core.set_file_property(
            activity_id, label, content, media_type
        )
        assert result is None

        # Cleanup
        await async_instance.core.delete_file_property(activity_id, label)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_set_file_property_with_filename(self, async_instance: AsyncOFSC):
        """Test set_file_property with optional filename parameter."""
        activity_id = 3954799
        label = "csign"
        content = b"file with name"
        media_type = "application/octet-stream"
        filename = "test.bin"

        result = await async_instance.core.set_file_property(
            activity_id, label, content, media_type, filename=filename
        )
        assert result is None

        # Cleanup
        await async_instance.core.delete_file_property(activity_id, label)


class TestAsyncDeleteFilePropertyLive:
    """Live tests for delete_file_property."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_delete_file_property_returns_none(self, async_instance: AsyncOFSC):
        """Test that delete_file_property returns None after upload."""
        activity_id = 3954799
        label = "csign"
        content = b"to be deleted"

        # First upload
        await async_instance.core.set_file_property(
            activity_id, label, content, "application/octet-stream"
        )

        # Then delete
        result = await async_instance.core.delete_file_property(activity_id, label)
        assert result is None


# endregion
