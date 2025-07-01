import asyncio
import os

import pytest

from ofsc.client import OFSC
from ofsc.models import CapacityArea
from ofsc.models.base import TranslationList
from ofsc.models.capacity import (
    CapacityCategory,
    CapacityAreaTimeInterval,
    CapacityAreaTimeIntervalListResponse,
    CapacityAreaTimeSlot,
    CapacityAreaTimeSlotListResponse,
    CapacityAreaWorkzone,
    CapacityAreaWorkzoneListResponse,
    CapacityAreaCategory,
    CapacityAreaCategoryListResponse,
    CapacityAreaOrganization,
    CapacityAreaOrganizationListResponse,
)
from ofsc.models.core import SubscriptionList, User, UserListResponse
from ofsc.models.metadata import (
    ActivityType,
    ActivityTypeGroup,
    ActivityTypeGroupItem,
    ActivityTypeGroupListResponse,
    Application,
    InventoryType,
    InventoryTypeListResponse,
    Organization,
    OrganizationListResponse,
    Property,
    PropertyListResponse,
    ResourceType,
    ResourceTypeListResponse,
    TimeSlot,
    TimeSlotListResponse,
    Workskill,
    WorkskillCondition,
    WorkskillConditionListResponse,
    WorkSkillGroup,
    WorkSkillGroupListResponse,
    WorkskillListResponse,
    Workzone,
    WorkzoneListResponse,
)


def get_test_data(collection: str, version: str = "25A") -> list:
    return (
        TEST_DATA.get(collection, [])
        if isinstance(TEST_DATA.get(collection), list)
        else [TEST_DATA.get(collection, "")]
    )


TEST_DATA = {
    # Existing with real IDs confirmed from response_examples
    "application": "demoauth",
    "activity_type_group": "customer",
    "activity_type": "LU",  # From 4_get_activity_types.json, first item
    "capacity_area": [
        "FLUSA",
        "CAUSA",
    ],  # From 14_get_capacity_areas.json, confirmed in existing array
    # New real IDs extracted from response_examples
    "capacity_category": "EST",  # From 23_get_capacity_categories.json
    "inventory_type": "FIT5000",  # From 31_get_inventory_types.json
    "organization": "default",  # From 46_get_organizations.json
    "property": "wie_wo_operation_id",  # From 50_get_properties.json
    "workskill_group": "",  # From 70_get_work_skill_groups.json - totalResults: 0, will skip
    "workskill": "EST",  # From 74_get_work_skills.json
}


@pytest.mark.live
class TestSunriseGetCollectionsMetadata:
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

    def test_sunrise_client_properties(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_properties = await client.metadata.get_properties()
                assert isinstance(response_properties, PropertyListResponse)
                assert response_properties.totalResults >= 100
                for prop in response_properties.items:
                    assert isinstance(prop, Property)
                    # Ensure all required fields are present
                    assert prop.label is not None
                    assert prop.name is not None
                    assert prop.entity is not None
                    assert prop.type is not None
                    assert prop.gui is not None
                    assert isinstance(prop.translations, TranslationList)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_resource_types(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_resource_types = await client.metadata.get_resource_types()
                assert isinstance(response_resource_types, ResourceTypeListResponse)
                assert response_resource_types.totalResults > 0
                for resource_type in response_resource_types.items:
                    assert isinstance(resource_type, ResourceType)
                    assert resource_type.label is not None
                    assert resource_type.name is not None
                    assert resource_type.active is not None
                    assert resource_type.role is not None
                    # THIS TEST IS CRITICAL TO DETECT CHANGES IN RESOURCE ROLES
                    assert resource_type.role in {
                        "field_resource",
                        "bucket",
                        "organization_unit",
                        "vehicle",
                        "warehouse",
                    }
                    assert isinstance(resource_type.translations, TranslationList)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_timeslots(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_timeslots = await client.metadata.get_timeslots()
                assert isinstance(response_timeslots, TimeSlotListResponse)
                assert response_timeslots.totalResults > 0
                for timeslot in response_timeslots.items:
                    assert isinstance(timeslot, TimeSlot)
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

    def test_sunrise_client_workskill_conditions(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_workskill_conditions = (
                    await client.metadata.get_workskill_conditions()
                )
                assert isinstance(
                    response_workskill_conditions, WorkskillConditionListResponse
                )
                assert response_workskill_conditions.totalResults > 0
                for condition in response_workskill_conditions.items:
                    assert isinstance(condition, WorkskillCondition)
                    assert condition.label is not None
                    assert condition.requiredLevel is not None
                    assert condition.preferableLevel is not None

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_workskill_groups(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_workskill_groups = await client.metadata.get_workskill_groups()
                assert isinstance(response_workskill_groups, WorkSkillGroupListResponse)
                # TODO: the SUNRISE Environment does not have a workskill group
                assert response_workskill_groups.totalResults > 0
                for group in response_workskill_groups.items:
                    assert isinstance(group, WorkSkillGroup)
                    assert group.label is not None
                    assert group.name is not None
                    assert group.active is not None

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_workskills(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_workskills = await client.metadata.get_workskills()
                assert isinstance(response_workskills, WorkskillListResponse)
                assert response_workskills.totalResults > 0
                for workskill in response_workskills.items:
                    assert isinstance(workskill, Workskill)
                    assert workskill.label is not None
                    assert workskill.name is not None
                    assert workskill.active is not None

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_workzones(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_workzones = await client.metadata.get_workzones()
                assert isinstance(response_workzones, WorkzoneListResponse)
                assert response_workzones.totalResults > 0
                for workzone in response_workzones.items:
                    assert isinstance(workzone, Workzone)
                    assert workzone.workZoneName is not None
                    assert workzone.workZoneLabel is not None
                    assert workzone.status is not None
                    assert workzone.status in {"active", "inactive"}
                    assert workzone.travelArea is not None
                    assert isinstance(workzone.keys, list)
                    if hasattr(workzone, "shapes"):
                        # Check if shapes is present and is a list
                        assert workzone.shapes is not None
                        assert isinstance(
                            workzone.shapes, list
                        )  # Assuming shapes is a list

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    # Individual Element Tests - Only for endpoints that exist in ENDPOINTS.md

    def test_sunrise_client_activity_type_groups_individual(
        self, async_client_basic_auth: OFSC
    ):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                identifiers = get_test_data("activity_type_group")
                for identifier in identifiers:
                    if identifier == "":
                        continue
                    group = await client.metadata.get_activity_type_group(identifier)
                    assert isinstance(group, ActivityTypeGroup)
                    assert group.label == identifier
                    assert group.name is not None
                    assert isinstance(group.translations, TranslationList)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_activity_types_individual(
        self, async_client_basic_auth: OFSC
    ):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                identifiers = get_test_data("activity_type")
                for identifier in identifiers:
                    if identifier == "":
                        continue
                    activity_type = await client.metadata.get_activity_type(identifier)
                    assert isinstance(activity_type, ActivityType)
                    assert activity_type.label == identifier
                    assert activity_type.name is not None
                    assert isinstance(activity_type.translations, TranslationList)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_applications_individual(
        self, async_client_basic_auth: OFSC
    ):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                identifiers = get_test_data("application")
                for identifier in identifiers:
                    if identifier == "":
                        continue
                    application = await client.metadata.get_application(identifier)
                    assert isinstance(application, Application)
                    assert application.label == identifier
                    assert application.name is not None

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_capacity_areas_individual(
        self, async_client_basic_auth: OFSC
    ):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                identifiers = get_test_data("capacity_area")
                for identifier in identifiers:
                    if identifier == "":
                        continue
                    area = await client.metadata.get_capacity_area(identifier)
                    assert isinstance(area, CapacityArea)
                    assert area.label == identifier
                    assert area.name is not None

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_capacity_categories_individual(
        self, async_client_basic_auth: OFSC
    ):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                identifiers = get_test_data("capacity_category")
                for identifier in identifiers:
                    if identifier == "":
                        continue
                    category = await client.metadata.get_capacity_category(identifier)
                    assert isinstance(category, CapacityCategory)
                    assert category.label == identifier
                    assert category.name is not None

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_inventory_types_individual(
        self, async_client_basic_auth: OFSC
    ):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                identifiers = get_test_data("inventory_type")
                for identifier in identifiers:
                    if identifier == "":
                        continue
                    inventory_type = await client.metadata.get_inventory_type(
                        identifier
                    )
                    assert isinstance(inventory_type, InventoryType)
                    assert inventory_type.label == identifier
                    assert inventory_type.name is not None
                    assert isinstance(inventory_type.translations, TranslationList)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_organizations_individual(
        self, async_client_basic_auth: OFSC
    ):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                identifiers = get_test_data("organization")
                for identifier in identifiers:
                    if identifier == "":
                        continue
                    organization = await client.metadata.get_organization(identifier)
                    assert isinstance(organization, Organization)
                    assert organization.label == identifier
                    assert organization.name is not None
                    assert isinstance(organization.translations, TranslationList)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_properties_individual(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                identifiers = get_test_data("property")
                for identifier in identifiers:
                    if identifier == "":
                        continue
                    property_obj = await client.metadata.get_property(identifier)
                    assert isinstance(property_obj, Property)
                    assert property_obj.label == identifier
                    assert property_obj.name is not None
                    assert isinstance(property_obj.translations, TranslationList)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_workskill_groups_individual(
        self, async_client_basic_auth: OFSC
    ):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                identifiers = get_test_data("workskill_group")
                for identifier in identifiers:
                    if identifier == "":
                        continue
                    workskill_group = await client.metadata.get_workskill_group(
                        identifier
                    )
                    assert isinstance(workskill_group, WorkSkillGroup)
                    assert workskill_group.label == identifier
                    assert workskill_group.name is not None

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_workskills_individual(self, async_client_basic_auth: OFSC):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                identifiers = get_test_data("workskill")
                for identifier in identifiers:
                    if identifier == "":
                        continue
                    workskill = await client.metadata.get_workskill(identifier)
                    assert isinstance(workskill, Workskill)
                    assert workskill.label == identifier
                    assert workskill.name is not None
                    assert isinstance(workskill.translations, TranslationList)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    # Capacity Area Sub-Resource Tests - Endpoints 16-21

    def test_sunrise_client_capacity_area_categories(
        self, async_client_basic_auth: OFSC
    ):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                capacity_area_identifiers = get_test_data("capacity_area")
                for area_identifier in capacity_area_identifiers:
                    if area_identifier == "":
                        continue
                    response = await client.metadata.get_capacity_area_categories(
                        area_identifier
                    )
                    assert isinstance(response, CapacityAreaCategoryListResponse)
                    assert response.totalResults >= 0
                    for category in response.items:
                        assert isinstance(category, CapacityAreaCategory)
                        assert category.label is not None
                        assert category.name is not None
                        # status field is optional but should be present in real data
                        if hasattr(category, "status"):
                            assert category.status in {"active", "inactive"}

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_capacity_area_workzones(
        self, async_client_basic_auth: OFSC
    ):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                capacity_area_identifiers = get_test_data("capacity_area")
                for area_identifier in capacity_area_identifiers:
                    if area_identifier == "":
                        continue
                    response = await client.metadata.get_capacity_area_workzones(
                        area_identifier
                    )
                    assert isinstance(response, CapacityAreaWorkzoneListResponse)
                    assert response.totalResults >= 0
                    for workzone in response.items:
                        assert isinstance(workzone, CapacityAreaWorkzone)
                        # v2 endpoint returns detailed workzone info
                        assert workzone.workZoneLabel is not None
                        assert workzone.workZoneName is not None

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_capacity_area_timeslots(
        self, async_client_basic_auth: OFSC
    ):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                capacity_area_identifiers = get_test_data("capacity_area")
                for area_identifier in capacity_area_identifiers:
                    if area_identifier == "":
                        continue
                    response = await client.metadata.get_capacity_area_timeslots(
                        area_identifier
                    )
                    assert isinstance(response, CapacityAreaTimeSlotListResponse)
                    assert response.totalResults >= 0
                    for timeslot in response.items:
                        assert isinstance(timeslot, CapacityAreaTimeSlot)
                        assert timeslot.label is not None
                        assert timeslot.name is not None
                        assert timeslot.timeFrom is not None
                        assert timeslot.timeTo is not None

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_capacity_area_timeintervals(
        self, async_client_basic_auth: OFSC
    ):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                capacity_area_identifiers = get_test_data("capacity_area")
                for area_identifier in capacity_area_identifiers:
                    if area_identifier == "":
                        continue
                    response = await client.metadata.get_capacity_area_timeintervals(
                        area_identifier
                    )
                    assert isinstance(response, CapacityAreaTimeIntervalListResponse)
                    assert response.totalResults >= 0
                    for timeinterval in response.items:
                        assert isinstance(timeinterval, CapacityAreaTimeInterval)
                        assert timeinterval.timeFrom is not None
                        # timeTo is optional - some intervals only have timeFrom
                        if timeinterval.timeTo is not None:
                            assert isinstance(timeinterval.timeTo, str)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_capacity_area_organizations(
        self, async_client_basic_auth: OFSC
    ):
        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                capacity_area_identifiers = get_test_data("capacity_area")
                for area_identifier in capacity_area_identifiers:
                    if area_identifier == "":
                        continue
                    response = await client.metadata.get_capacity_area_organizations(
                        area_identifier
                    )
                    assert isinstance(response, CapacityAreaOrganizationListResponse)
                    assert response.totalResults >= 0
                    for organization in response.items:
                        assert isinstance(organization, CapacityAreaOrganization)
                        assert organization.label is not None
                        assert organization.name is not None
                        assert organization.type is not None
                        assert organization.type in {"contractor", "inhouse"}

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))
