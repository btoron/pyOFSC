"""
Tests for routing profiles metadata API

Tests follow TDD methodology for GET operations first, then PUT/POST operations.
"""

from ofsc.common import FULL_RESPONSE, OBJ_RESPONSE
from ofsc.models import (
    RoutingProfile,
    RoutingProfileList,
    RoutingPlan,
    RoutingPlanList,
    RoutingPlanData,
)


# Phase 1: GET Operations Tests


def test_get_routing_profiles_basic(instance):
    """Test basic GET routing profiles with full response"""
    response = instance.metadata.get_routing_profiles(response_type=FULL_RESPONSE)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_get_routing_profiles_obj(instance):
    """Test GET routing profiles returning model object"""
    response = instance.metadata.get_routing_profiles()
    assert isinstance(response, RoutingProfileList)
    assert hasattr(response, "items")
    assert hasattr(response, "totalResults")


def test_get_routing_profiles_validation(instance):
    """Test routing profiles response structure and validation"""
    response = instance.metadata.get_routing_profiles(response_type=FULL_RESPONSE)
    data = response.json()

    # Validate pagination fields
    assert "totalResults" in data
    assert "hasMore" in data
    assert "limit" in data
    assert "offset" in data

    # Validate items structure
    if data["totalResults"] > 0:
        first_item = data["items"][0]
        assert "profileLabel" in first_item


def test_get_routing_profile_plans_basic(instance):
    """Test basic GET routing profile plans with full response"""
    # First get a profile to test with
    profiles_response = instance.metadata.get_routing_profiles(
        response_type=FULL_RESPONSE
    )
    profiles_data = profiles_response.json()

    # Skip if no profiles available
    if profiles_data["totalResults"] == 0:
        return

    profile_label = profiles_data["items"][0]["profileLabel"]

    # Test getting plans for the profile
    response = instance.metadata.get_routing_profile_plans(
        profile_label=profile_label, response_type=FULL_RESPONSE
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_get_routing_profile_plans_obj(instance):
    """Test GET routing profile plans returning model object"""
    # First get a profile to test with
    profiles_response = instance.metadata.get_routing_profiles()

    # Skip if no profiles available
    if len(profiles_response.items) == 0:
        return

    profile_label = profiles_response.items[0].profileLabel

    # Test getting plans for the profile
    response = instance.metadata.get_routing_profile_plans(
        profile_label=profile_label
    )
    assert isinstance(response, RoutingPlanList)
    assert hasattr(response, "items")
    assert hasattr(response, "totalResults")


def test_get_routing_profile_plans_validation(instance):
    """Test routing plans response structure and validation"""
    # First get a profile to test with
    profiles_response = instance.metadata.get_routing_profiles(
        response_type=FULL_RESPONSE
    )
    profiles_data = profiles_response.json()

    # Skip if no profiles available
    if profiles_data["totalResults"] == 0:
        return

    profile_label = profiles_data["items"][0]["profileLabel"]

    # Test getting plans for the profile
    response = instance.metadata.get_routing_profile_plans(
        profile_label=profile_label, response_type=FULL_RESPONSE
    )
    data = response.json()

    # Validate pagination fields
    assert "totalResults" in data
    assert "hasMore" in data
    assert "limit" in data
    assert "offset" in data

    # Validate items structure if plans exist
    if data["totalResults"] > 0:
        first_item = data["items"][0]
        assert "planLabel" in first_item


def test_export_routing_plan_basic(instance):
    """Test basic routing plan export returns parsed Pydantic model"""
    # First get a profile and plan to test with
    profiles_response = instance.metadata.get_routing_profiles(
        response_type=FULL_RESPONSE
    )
    profiles_data = profiles_response.json()

    # Skip if no profiles available
    if profiles_data["totalResults"] == 0:
        return

    profile_label = profiles_data["items"][0]["profileLabel"]

    # Get plans for the profile
    plans_response = instance.metadata.get_routing_profile_plans(
        profile_label=profile_label, response_type=FULL_RESPONSE
    )
    plans_data = plans_response.json()

    # Skip if no plans available
    if plans_data["totalResults"] == 0:
        return

    plan_label = plans_data["items"][0]["planLabel"]

    # Test exporting the plan with FULL_RESPONSE
    response = instance.metadata.export_routing_plan(
        profile_label=profile_label, plan_label=plan_label, response_type=FULL_RESPONSE
    )
    assert response.status_code == 200
    # Verify response structure
    data = response.json()
    assert "routing_plan" in data
    assert "sign" in data
    assert "version" in data


def test_export_routing_plan_obj(instance):
    """Test routing plan export returning RoutingPlanData model"""
    # First get a profile and plan to test with
    profiles_response = instance.metadata.get_routing_profiles()

    # Skip if no profiles available
    if len(profiles_response.items) == 0:
        return

    profile_label = profiles_response.items[0].profileLabel

    # Get plans for the profile
    plans_response = instance.metadata.get_routing_profile_plans(
        profile_label=profile_label
    )

    # Skip if no plans available
    if len(plans_response.items) == 0:
        return

    plan_label = plans_response.items[0].planLabel

    # Test exporting the plan - returns RoutingPlanData model
    response = instance.metadata.export_routing_plan(
        profile_label=profile_label, plan_label=plan_label
    )
    assert isinstance(response, RoutingPlanData)
    # Verify model structure and access
    assert hasattr(response, "routing_plan")
    assert hasattr(response, "sign")
    assert hasattr(response, "version")
    # Access routing plan fields with type safety
    assert response.routing_plan.rpname is not None
    assert response.routing_plan.rpoptimization in ["fastest", "balanced", "best"]


def test_export_routing_plan_validation(instance):
    """Test routing plan Pydantic model validation and nested structure"""
    # First get a profile and plan to test with
    profiles_response = instance.metadata.get_routing_profiles()

    # Skip if no profiles available
    if len(profiles_response.items) == 0:
        return

    profile_label = profiles_response.items[0].profileLabel

    # Get plans for the profile
    plans_response = instance.metadata.get_routing_profile_plans(
        profile_label=profile_label
    )

    # Skip if no plans available
    if len(plans_response.items) == 0:
        return

    plan_label = plans_response.items[0].planLabel

    # Test exporting the plan - returns RoutingPlanData model
    plan_data = instance.metadata.export_routing_plan(
        profile_label=profile_label, plan_label=plan_label
    )

    # Validate nested structure access
    assert isinstance(plan_data.routing_plan.activityGroups, list)

    # If there are activity groups, validate their structure
    if len(plan_data.routing_plan.activityGroups) > 0:
        first_group = plan_data.routing_plan.activityGroups[0]
        # Access activity group fields
        assert hasattr(first_group, "activity_location")
        assert hasattr(first_group, "filterLabel")
        assert isinstance(first_group.providerGroups, list)

        # If there are provider groups, validate their structure
        if len(first_group.providerGroups) > 0:
            first_provider = first_group.providerGroups[0]
            assert hasattr(first_provider, "priority")
            assert hasattr(first_provider, "filterLabel")


# Phase 2: PUT/POST Operations Tests (to be implemented later)
# TODO: Add import_routing_plan tests
# TODO: Add force_import_routing_plan tests
# TODO: Add start_routing_plan tests
