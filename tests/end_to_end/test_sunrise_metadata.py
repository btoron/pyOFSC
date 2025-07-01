import asyncio
import os

import pytest

from ofsc.client import OFSC
from ofsc.models import CapacityArea, EnumerationValue
from ofsc.models.base import TranslationList
from ofsc.models.capacity import (
    CapacityAreaCategory,
    CapacityAreaCategoryListResponse,
    CapacityAreaOrganization,
    CapacityAreaOrganizationListResponse,
    CapacityAreaTimeInterval,
    CapacityAreaTimeIntervalListResponse,
    CapacityAreaTimeSlot,
    CapacityAreaTimeSlotListResponse,
    CapacityAreaWorkzone,
    CapacityAreaWorkzoneListResponse,
    CapacityCategory,
)
from ofsc.models.core import SubscriptionList, User, UserListResponse
from ofsc.models.metadata import (
    ActivityType,
    ActivityTypeGroup,
    ActivityTypeGroupItem,
    ActivityTypeGroupListResponse,
    ApiAccessStatus,
    Application,
    ApplicationApiAccess,
    ApplicationApiAccessListResponse,
    EnumerationValueList,
    Form,
    FormListResponse,
    InventoryType,
    InventoryTypeListResponse,
    Language,
    LanguageListResponse,
    LinkTemplate,
    LinkTemplateListResponse,
    NonWorkingReason,
    NonWorkingReasonListResponse,
    Organization,
    OrganizationListResponse,
    Property,
    PropertyListResponse,
    ResourceType,
    ResourceTypeListResponse,
    RoutingProfile,
    RoutingProfileListResponse,
    RoutingPlan,
    RoutingPlanListResponse,
    Shift,
    ShiftListResponse,
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
    "enumerated_property": "complete_code",  # From 54_get_property_enumeration.json
    "workskill_group": "",  # From 70_get_work_skill_groups.json - totalResults: 0, will skip
    "workskill": "EST",  # From 74_get_work_skills.json
    # New endpoints from collected responses
    "form": "mobile_provider_request#8#",  # From 27_get_forms.json
    "link_template": "start-after",  # From 35_get_link_templates.json
    "routing_profile": "MaintenanceRoutingProfile",  # From 57_get_routing_profiles.json
    "routing_plan": "Optimization",  # From 58_get_routingProfiles_MaintenanceRoutingProfile_plans.json
    "shift": "20-05",  # From 64_get_shift.json (individual response)
    "workzone": "ALTAMONTE_SPRINGS",  # From 82_get_workzone.json
}


@pytest.mark.live
class TestSunriseGetCollectionsMetadata:
    """Live authentication tests using OFSC client classes.

    Implemented metadata endpoints NOT tested in this file:

    API Access Endpoints:
    - ID 11: GET /rest/ofscMetadata/v1/applications/{label}/apiAccess/{apiLabel}

    Note: These endpoints are implemented in the client but not covered by end-to-end tests.
    Consider adding tests for these endpoints in future test coverage improvements.
    """

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
        """Test basic client functionality with subscriptions and users."""

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
        """Test endpoint ID 1: GET /rest/ofscMetadata/v1/activityTypeGroups - Get activity type groups list."""

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
        """Test endpoint ID 4: GET /rest/ofscMetadata/v1/activityTypes - Get activity types list."""

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
        """Test endpoint ID 7: GET /rest/ofscMetadata/v1/applications - Get applications list."""

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
        """Test endpoint ID 14: GET /rest/ofscMetadata/v1/capacityAreas - Get capacity areas list."""

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
        """Test endpoint ID 23: GET /rest/ofscMetadata/v1/capacityCategories - Get capacity categories list."""

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
        """Test endpoint ID 31: GET /rest/ofscMetadata/v1/inventoryTypes - Get inventory types list."""

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
        """Test endpoint ID 46: GET /rest/ofscMetadata/v1/organizations - Get organizations list."""

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
        """Test endpoint ID 50: GET /rest/ofscMetadata/v1/properties - Get properties list."""

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
        """Test endpoint ID 56: GET /rest/ofscMetadata/v1/resourceTypes - Get resource types list."""

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
        """Test endpoint ID 67: GET /rest/ofscMetadata/v1/timeSlots - Get time slots list."""

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
        """Test endpoint ID 68: GET /rest/ofscMetadata/v1/workSkillConditions - Get work skill conditions list."""

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
        """Test endpoint ID 70: GET /rest/ofscMetadata/v1/workSkillGroups - Get work skill groups list."""

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
        """Test endpoint ID 74: GET /rest/ofscMetadata/v1/workSkills - Get work skills list."""

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
        """Test endpoint ID 78: GET /rest/ofscMetadata/v1/workZones - Get work zones list."""

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

    def test_sunrise_client_forms(self, async_client_basic_auth: OFSC):
        """Test endpoint ID 27: GET /rest/ofscMetadata/v1/forms - Get forms list."""

        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_forms = await client.metadata.get_forms()
                assert isinstance(response_forms, FormListResponse)
                assert response_forms.totalResults > 0
                for form in response_forms.items:
                    assert isinstance(form, Form)
                    assert form.label is not None
                    assert form.name is not None
                    assert isinstance(form.translations, TranslationList)
                    assert isinstance(form.links, list)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_link_templates(self, async_client_basic_auth: OFSC):
        """Test endpoint ID 35: GET /rest/ofscMetadata/v1/linkTemplates - Get link templates list."""

        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_templates = await client.metadata.get_link_templates()
                assert isinstance(response_templates, LinkTemplateListResponse)
                assert response_templates.totalResults > 0
                for template in response_templates.items:
                    assert isinstance(template, LinkTemplate)
                    assert template.label is not None
                    assert template.active is not None
                    assert isinstance(template.translations, list)
                    assert isinstance(template.links, list)
                    # Optional fields that may not be present for all templates
                    if template.reverseLabel is not None:
                        assert isinstance(template.reverseLabel, str)
                    if template.linkType is not None:
                        assert isinstance(template.linkType, str)
                    if template.minInterval is not None:
                        assert isinstance(template.minInterval, str)
                    if template.maxInterval is not None:
                        assert isinstance(template.maxInterval, str)
                    if template.minIntervalValue is not None:
                        assert isinstance(template.minIntervalValue, int)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_routing_profiles(self, async_client_basic_auth: OFSC):
        """Test endpoint ID 57: GET /rest/ofscMetadata/v1/routingProfiles - Get routing profiles list."""

        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_profiles = await client.metadata.get_routing_profiles()
                assert isinstance(response_profiles, RoutingProfileListResponse)
                assert response_profiles.totalResults > 0
                for profile in response_profiles.items:
                    assert isinstance(profile, RoutingProfile)
                    assert profile.profileLabel is not None

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_routing_profile_plans(self, async_client_basic_auth: OFSC):
        """Test endpoint ID 58: GET /rest/ofscMetadata/v1/routingProfiles/{profileLabel}/plans - Get routing plans for a routing profile."""
        identifier = get_test_data("routing_profile")[0]

        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_plans = await client.metadata.get_routing_profile_plans(identifier)
                assert isinstance(response_plans, RoutingPlanListResponse)
                assert response_plans.totalResults > 0
                for plan in response_plans.items:
                    assert isinstance(plan, RoutingPlan)
                    assert plan.planLabel is not None
                    assert len(plan.planLabel) > 0

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_languages(self, async_client_basic_auth: OFSC):
        """Test endpoint ID 34: GET /rest/ofscMetadata/v1/languages - Get languages list."""

        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_languages = await client.metadata.get_languages()
                assert isinstance(response_languages, LanguageListResponse)
                assert response_languages.totalResults > 0
                for language in response_languages.items:
                    assert isinstance(language, Language)
                    assert language.label is not None
                    assert language.code is not None
                    assert language.name is not None
                    assert language.active is not None
                    assert isinstance(language.translations, TranslationList)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_non_working_reasons(self, async_client_basic_auth: OFSC):
        """Test endpoint ID 45: GET /rest/ofscMetadata/v1/nonWorkingReasons - Get non-working reasons list."""

        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_reasons = await client.metadata.get_non_working_reasons()
                assert isinstance(response_reasons, NonWorkingReasonListResponse)
                assert response_reasons.totalResults > 0
                for reason in response_reasons.items:
                    assert isinstance(reason, NonWorkingReason)
                    assert reason.label is not None
                    assert reason.name is not None
                    assert reason.active is not None
                    assert isinstance(reason.translations, TranslationList)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_property_enumeration(self, async_client_basic_auth: OFSC):
        """Test endpoint ID 54: GET /rest/ofscMetadata/v1/properties/{label}/enumerationList - Get property enumeration values."""

        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                property_identifiers = get_test_data("enumerated_property")
                for identifier in property_identifiers:
                    if identifier == "":
                        continue
                    response_enumeration = await client.metadata.get_enumeration_values(identifier)
                    assert isinstance(response_enumeration, EnumerationValueList)
                    assert response_enumeration.totalResults > 0  # We expect enumeration values
                    for value in response_enumeration.items:
                        assert isinstance(value, EnumerationValue)
                        assert value.label is not None
                        assert value.active is not None
                        # Verify translations are present (this is where the actual names are)
                        assert value.translations is not None
                        assert isinstance(value.translations, TranslationList)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_shifts(self, async_client_basic_auth: OFSC):
        """Test endpoint ID 63: GET /rest/ofscMetadata/v1/shifts - Get shifts list."""

        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                response_shifts = await client.metadata.get_shifts()
                assert isinstance(response_shifts, ShiftListResponse)
                assert response_shifts.totalResults >= 0
                for shift in response_shifts.items:
                    assert isinstance(shift, Shift)
                    assert shift.label is not None
                    assert shift.name is not None
                    assert shift.active is not None
                    assert shift.type is not None

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    # Individual Element Tests - Only for endpoints that exist in ENDPOINTS.md

    def test_sunrise_client_activity_type_groups_individual(
        self, async_client_basic_auth: OFSC
    ):
        """Test endpoint ID 2: GET /rest/ofscMetadata/v1/activityTypeGroups/{label} - Get individual activity type group."""

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
        """Test endpoint ID 5: GET /rest/ofscMetadata/v1/activityTypes/{label} - Get individual activity type."""

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
        """Test endpoint ID 8: GET /rest/ofscMetadata/v1/applications/{label} - Get individual application."""

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
        """Test endpoint ID 15: GET /rest/ofscMetadata/v1/capacityAreas/{label} - Get individual capacity area."""

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
        """Test endpoint ID 24: GET /rest/ofscMetadata/v1/capacityCategories/{label} - Get individual capacity category."""

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
        """Test endpoint ID 32: GET /rest/ofscMetadata/v1/inventoryTypes/{label} - Get individual inventory type."""

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
        """Test endpoint ID 47: GET /rest/ofscMetadata/v1/organizations/{label} - Get individual organization."""

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
        """Test endpoint ID 51: GET /rest/ofscMetadata/v1/properties/{label} - Get individual property."""

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
        """Test endpoint ID 71: GET /rest/ofscMetadata/v1/workSkillGroups/{label} - Get individual work skill group."""

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
        """Test endpoint ID 75: GET /rest/ofscMetadata/v1/workSkills/{label} - Get individual work skill."""

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

    def test_sunrise_client_forms_individual(self, async_client_basic_auth: OFSC):
        """Test endpoint ID 28: GET /rest/ofscMetadata/v1/forms/{label} - Get individual form."""

        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                identifiers = get_test_data("form")
                for identifier in identifiers:
                    if identifier == "":
                        continue
                    form = await client.metadata.get_form(identifier)
                    assert isinstance(form, Form)
                    assert form.label == identifier
                    assert form.name is not None
                    assert isinstance(form.translations, TranslationList)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_link_templates_individual(
        self, async_client_basic_auth: OFSC
    ):
        """Test endpoint ID 36: GET /rest/ofscMetadata/v1/linkTemplates/{label} - Get individual link template."""

        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                identifiers = get_test_data("link_template")
                for identifier in identifiers:
                    if identifier == "":
                        continue
                    template = await client.metadata.get_link_template(identifier)
                    assert isinstance(template, LinkTemplate)
                    assert template.label == identifier
                    assert template.active is not None
                    assert isinstance(template.translations, list)
                    # Optional fields that may not be present for all templates
                    if template.reverseLabel is not None:
                        assert isinstance(template.reverseLabel, str)
                    if template.linkType is not None:
                        assert isinstance(template.linkType, str)
                    if template.minInterval is not None:
                        assert isinstance(template.minInterval, str)
                    if template.maxInterval is not None:
                        assert isinstance(template.maxInterval, str)
                    if template.minIntervalValue is not None:
                        assert isinstance(template.minIntervalValue, int)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_shifts_individual(self, async_client_basic_auth: OFSC):
        """Test endpoint ID 64: GET /rest/ofscMetadata/v1/shifts/{label} - Get individual shift."""

        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                identifiers = get_test_data("shift")
                for identifier in identifiers:
                    if identifier == "":
                        continue
                    shift = await client.metadata.get_shift(identifier)
                    assert isinstance(shift, Shift)
                    assert shift.label == identifier
                    assert shift.name is not None
                    assert shift.active is not None
                    assert shift.type is not None
                    # Optional fields that may be present
                    if shift.points is not None:
                        assert isinstance(shift.points, int)
                    if shift.workTimeStart is not None:
                        assert isinstance(shift.workTimeStart, str)
                    if shift.workTimeEnd is not None:
                        assert isinstance(shift.workTimeEnd, str)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_workzones_individual(self, async_client_basic_auth: OFSC):
        """Test endpoint ID 82: GET /rest/ofscMetadata/v1/workZones/{label} - Get individual work zone."""

        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                identifiers = get_test_data("workzone")
                for identifier in identifiers:
                    if identifier == "":
                        continue
                    workzone = await client.metadata.get_workzone(identifier)
                    assert isinstance(workzone, Workzone)
                    assert workzone.workZoneLabel == identifier
                    assert workzone.workZoneName is not None
                    assert workzone.status is not None
                    assert workzone.status in {"active", "inactive"}
                    assert workzone.travelArea is not None
                    assert isinstance(workzone.keys, list)
                    if hasattr(workzone, "shapes") and workzone.shapes is not None:
                        assert isinstance(workzone.shapes, list)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    # Capacity Area Sub-Resource Tests - Endpoints 16-21

    def test_sunrise_client_capacity_area_categories(
        self, async_client_basic_auth: OFSC
    ):
        """Test endpoint ID 16: GET /rest/ofscMetadata/v1/capacityAreas/{label}/capacityCategories - Get capacity area categories."""

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
        """Test endpoint ID 17: GET /rest/ofscMetadata/v2/capacityAreas/{label}/workZones - Get capacity area work zones (v2)."""

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
        """Test endpoint ID 19: GET /rest/ofscMetadata/v1/capacityAreas/{label}/timeSlots - Get capacity area time slots."""

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
        """Test endpoint ID 20: GET /rest/ofscMetadata/v1/capacityAreas/{label}/timeIntervals - Get capacity area time intervals."""

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
        """Test endpoint ID 21: GET /rest/ofscMetadata/v1/capacityAreas/{label}/organizations - Get capacity area organizations."""

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

    def test_sunrise_client_application_api_accesses(self, async_client_basic_auth: OFSC):
        """Test endpoint ID 10: GET /rest/ofscMetadata/v1/applications/{label}/apiAccess - Get application API accesses."""

        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                application_identifiers = get_test_data("application")
                for identifier in application_identifiers:
                    if identifier == "":
                        continue
                    response = await client.metadata.get_application_api_accesses(identifier)
                    assert isinstance(response, ApplicationApiAccessListResponse)
                    assert response.totalResults > 0  # Expect at least some API accesses
                    
                    for api_access in response.items:
                        assert isinstance(api_access, ApplicationApiAccess)
                        assert api_access.label is not None
                        assert api_access.name is not None
                        # Validate enum constraints
                        assert api_access.status in {ApiAccessStatus.ACTIVE, ApiAccessStatus.INACTIVE}
                        assert isinstance(api_access.links, list)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_application_api_access_individual(self, async_client_basic_auth: OFSC):
        """Test endpoint ID 11: GET /rest/ofscMetadata/v1/applications/{label}/apiAccess/{apiLabel} - Get individual API access."""

        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                application_identifiers = get_test_data("application")
                for identifier in application_identifiers:
                    if identifier == "":
                        continue
                    # Test with a known API access label
                    api_access = await client.metadata.get_application_api_access(identifier, "metadataAPI")
                    assert isinstance(api_access, ApplicationApiAccess)
                    assert api_access.label == "metadataAPI"
                    assert api_access.name is not None
                    assert api_access.status in {ApiAccessStatus.ACTIVE, ApiAccessStatus.INACTIVE}
                    assert isinstance(api_access.links, list)

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))
