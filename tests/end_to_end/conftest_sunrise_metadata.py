"""Shared fixtures and test data for Sunrise metadata end-to-end tests.

This module provides common fixtures and test data used by both GET and PUT
metadata test files to avoid duplication and ensure consistency.
"""


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
    "activity_type": [
        "LU",
        "01",
        "03",
        "05",
    ],  # From 4_get_activity_types.json, first item
    "capacity_area": [
        "FLUSA",
        "CAUSA",
    ],  # From 14_get_capacity_areas.json, confirmed in existing array
    # New real IDs extracted from response_examples
    "capacity_category": ["EST", "RES", "COM"],  # From 23_get_capacity_categories.json
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
    "timeslot": ["08-10", "10-12"],  # From 86_get_timeslots.json
}


# Note: live_credentials and async_client_basic_auth fixtures are now available
# from the main tests/conftest.py file
