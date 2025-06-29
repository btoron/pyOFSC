import asyncio
import os

import pytest

from ofsc.client import OFSC
from ofsc.models import CapacityArea
from ofsc.models.base import TranslationList
from ofsc.models.capacity import CapacityCategory
from ofsc.models.core import SubscriptionList, User, UserListResponse
from ofsc.models.metadata import (
    ActivityTypeGroup,
    ActivityTypeGroupItem,
    ActivityTypeGroupListResponse,
    Application,
    InventoryType,
    InventoryTypeListResponse,
    Organization,
    OrganizationListResponse,
    TimeSlotListResponse,
)


@pytest.mark.live
class TestSunriseAuthentication:
    """Live authentication tests using OFSC client classes."""

    @pytest.fixture
    def live_credentials(self):
        """Get live credentials from environment variables."""
        instance = os.getenv("OFSC_INSTANCE")
        client_id = os.getenv("OFSC_CLIENT_ID")
        client_secret = os.getenv("OFSC_CLIENT_SECRET")

        if not all([instance, client_id, client_secret]):
            pytest.skip(
                "Live credentials not available. Set OFSC_INSTANCE, OFSC_CLIENT_ID, OFSC_CLIENT_SECRET"
            )

        return {
            "instance": instance,
            "client_id": client_id,
            "client_secret": client_secret,
        }

    @pytest.fixture
    def async_client_basic_auth(self, live_credentials):
        """Async OFSC client with Basic Auth for live testing."""
        return OFSC(
            instance=live_credentials["instance"],
            client_id=live_credentials["client_id"],
            client_secret=live_credentials["client_secret"],
            use_token=False,  # Use Basic Auth
        )

    def test_full_client(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                # Test if the client can fetch subscriptions
                subscription_response: SubscriptionList = (
                    await client.core.get_subscriptions()
                )
                # Optionally, print the first subscriptio for debugging
                assert subscription_response.totalResults >= 0
                response: UserListResponse = await client.core.get_users()
                assert response.totalResults == 100
                for user in response.users:
                    assert isinstance(user, User)
                response_timeslots = await client.metadata.get_timeslots()
                assert isinstance(response_timeslots, TimeSlotListResponse)
                assert response_timeslots.totalResults >= 0
                for timeslot in response_timeslots.items:
                    assert timeslot.isAllDay is not None
                    if timeslot.isAllDay:
                        # All-day slots should have no time bounds
                        assert timeslot.timeStart is None
                        assert timeslot.timeEnd is None
                    else:
                        # Timed slots should have both time bounds
                        assert timeslot.timeStart is not None
                        assert timeslot.timeEnd is not None

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_activity_typegroups(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_typegroups: ActivityTypeGroupListResponse = (
                    await client.metadata.get_activity_type_groups()
                )
                assert response_typegroups.totalResults >= 0
                for group in response_typegroups.items:
                    assert isinstance(group, ActivityTypeGroup)
                    assert group.label is not None
                    assert group.name is not None
                    assert group.activityTypes is not None
                    for activityType in group.activityTypes:
                        assert isinstance(activityType, ActivityTypeGroupItem)
                        assert activityType.label is not None

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_activity_types(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_types = await client.metadata.get_activity_types()
                assert response_types.totalResults > 0
                for activity_type in response_types.items:
                    assert activity_type.label is not None
                    assert activity_type.name is not None
                    assert isinstance(activity_type.translations, TranslationList)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_applications(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_apps = await client.metadata.get_applications()
                assert response_apps.totalResults > 0
                for app in response_apps.items:
                    assert isinstance(app, Application)
                    assert app.label is not None
                    assert app.name is not None

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_capacity_areas(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_areas = await client.metadata.get_capacity_areas(
                    expandParent=True,
                    fields="label, name, type, status, parent.name, parent.label".split(
                        ", "
                    ),
                )
                assert response_areas.totalResults > 0
                for area in response_areas.items:
                    assert isinstance(area, CapacityArea)
                    assert area.label is not None
                    assert area.name is not None
                    assert area.type in {"area", "group"}
                    assert area.status in {"active", "inactive"}

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_capacity_categories(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_categories = await client.metadata.get_capacity_categories()
                assert response_categories.totalResults > 0
                for category in response_categories.items:
                    assert isinstance(category, CapacityCategory)
                    assert category.label is not None
                    assert category.name is not None
                    assert category.active is not None
                    assert category.timeSlots is not None
                    assert category.translations is not None
                    assert category.workSkills is not None
                    assert category.workSkillGroups is not None

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_inventory_types(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_inventory = await client.metadata.get_inventory_types()
                assert response_inventory.totalResults > 0
                assert isinstance(response_inventory, InventoryTypeListResponse)
                for inventory in response_inventory.items:
                    assert isinstance(inventory, InventoryType)
                    assert inventory.label is not None
                    assert inventory.name is not None
                    assert inventory.active is not None
                    assert inventory.translations is not None
                    assert isinstance(inventory.translations, TranslationList)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_organizations(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_orgs = await client.metadata.get_organizations()
                assert isinstance(response_orgs, OrganizationListResponse)
                assert response_orgs.totalResults > 0
                for org in response_orgs.items:
                    assert isinstance(org, Organization)
                    assert org.label is not None
                    assert org.name is not None
                    assert isinstance(org.translations, TranslationList)
                    assert org.type in {"contractor", "inhouse"}

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))
