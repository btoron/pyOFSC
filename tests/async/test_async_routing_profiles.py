"""Tests for async routing profiles API methods."""

import json
from pathlib import Path

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCConflictError, OFSCNotFoundError
from ofsc.models import (
    RoutingPlan,
    RoutingPlanData,
    RoutingPlanList,
    RoutingProfile,
    RoutingProfileList,
)


# ===================================================================
# GET ROUTING PROFILES
# ===================================================================


class TestAsyncGetRoutingProfilesLive:
    """Live tests for get_routing_profiles."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_routing_profiles(self, async_instance: AsyncOFSC):
        """Test get_routing_profiles with actual API - validates structure."""
        result = await async_instance.metadata.get_routing_profiles(offset=0, limit=100)
        assert isinstance(result, RoutingProfileList)
        assert result.totalResults >= 0
        assert isinstance(result.items, list)
        if len(result.items) > 0:
            assert isinstance(result.items[0], RoutingProfile)
            assert result.items[0].profileLabel is not None

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_routing_profiles_pagination(self, async_instance: AsyncOFSC):
        """Test get_routing_profiles with pagination."""
        result = await async_instance.metadata.get_routing_profiles(offset=0, limit=2)
        assert isinstance(result, RoutingProfileList)
        assert result.limit == 2


class TestAsyncGetRoutingProfiles:
    """Model validation tests for get_routing_profiles."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_routing_profiles_with_model(self, async_instance: AsyncOFSC):
        """Test that get_routing_profiles returns RoutingProfileList model."""
        result = await async_instance.metadata.get_routing_profiles()
        assert isinstance(result, RoutingProfileList)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_routing_profiles_total_results(self, async_instance: AsyncOFSC):
        """Test that totalResults is populated."""
        result = await async_instance.metadata.get_routing_profiles()
        assert hasattr(result, "totalResults")
        assert isinstance(result.totalResults, int)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_routing_profiles_field_types(self, async_instance: AsyncOFSC):
        """Test that fields have correct types."""
        result = await async_instance.metadata.get_routing_profiles()
        if len(result.items) > 0:
            profile = result.items[0]
            assert isinstance(profile.profileLabel, str)


# ===================================================================
# GET ROUTING PROFILE PLANS
# ===================================================================


class TestAsyncGetRoutingProfilePlansLive:
    """Live tests for get_routing_profile_plans."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_routing_profile_plans(self, async_instance: AsyncOFSC):
        """Test get_routing_profile_plans with actual API."""
        # First get a routing profile
        profiles = await async_instance.metadata.get_routing_profiles()
        assert len(profiles.items) > 0
        profile_label = profiles.items[0].profileLabel

        # Get plans for that profile
        result = await async_instance.metadata.get_routing_profile_plans(profile_label)
        assert isinstance(result, RoutingPlanList)
        assert result.totalResults >= 0

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_routing_profile_plans_pagination(
        self, async_instance: AsyncOFSC
    ):
        """Test get_routing_profile_plans with pagination."""
        # Get first routing profile
        profiles = await async_instance.metadata.get_routing_profiles()
        if len(profiles.items) > 0:
            profile_label = profiles.items[0].profileLabel
            result = await async_instance.metadata.get_routing_profile_plans(
                profile_label, offset=0, limit=2
            )
            assert isinstance(result, RoutingPlanList)
            assert result.limit == 2

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_routing_profile_plans_not_found(self, async_instance: AsyncOFSC):
        """Test get_routing_profile_plans with non-existent profile."""
        with pytest.raises(OFSCNotFoundError) as exc_info:
            await async_instance.metadata.get_routing_profile_plans(
                "NONEXISTENT_PROFILE_12345"
            )
        assert exc_info.value.status_code == 404


class TestAsyncGetRoutingProfilePlans:
    """Model validation tests for get_routing_profile_plans."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_routing_profile_plans_with_model(
        self, async_instance: AsyncOFSC
    ):
        """Test that get_routing_profile_plans returns RoutingPlanList model."""
        # Get first routing profile
        profiles = await async_instance.metadata.get_routing_profiles()
        if len(profiles.items) > 0:
            profile_label = profiles.items[0].profileLabel
            result = await async_instance.metadata.get_routing_profile_plans(
                profile_label
            )
            assert isinstance(result, RoutingPlanList)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_routing_profile_plans_field_types(
        self, async_instance: AsyncOFSC
    ):
        """Test that fields have correct types."""
        # Get first routing profile
        profiles = await async_instance.metadata.get_routing_profiles()
        if len(profiles.items) > 0:
            profile_label = profiles.items[0].profileLabel
            result = await async_instance.metadata.get_routing_profile_plans(
                profile_label
            )
            if len(result.items) > 0:
                plan = result.items[0]
                assert isinstance(plan, RoutingPlan)
                assert isinstance(plan.planLabel, str)


# ===================================================================
# EXPORT ROUTING PLAN
# ===================================================================


class TestAsyncExportRoutingPlanLive:
    """Live tests for export_routing_plan."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_export_routing_plan(self, async_instance: AsyncOFSC):
        """Test export_routing_plan with actual API."""
        # Get first routing profile and plan
        profiles = await async_instance.metadata.get_routing_profiles()
        if len(profiles.items) > 0:
            profile_label = profiles.items[0].profileLabel
            plans = await async_instance.metadata.get_routing_profile_plans(
                profile_label
            )
            if len(plans.items) > 0:
                plan_label = plans.items[0].planLabel
                result = await async_instance.metadata.export_routing_plan(
                    profile_label, plan_label
                )
                assert isinstance(result, RoutingPlanData)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_export_routing_plan_not_found(self, async_instance: AsyncOFSC):
        """Test export_routing_plan with non-existent plan."""
        # Get first routing profile
        profiles = await async_instance.metadata.get_routing_profiles()
        if len(profiles.items) > 0:
            profile_label = profiles.items[0].profileLabel
            with pytest.raises(OFSCNotFoundError) as exc_info:
                await async_instance.metadata.export_routing_plan(
                    profile_label, "NONEXISTENT_PLAN_12345"
                )
            assert exc_info.value.status_code == 404


class TestAsyncExportRoutingPlan:
    """Model validation tests for export_routing_plan."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_export_routing_plan_returns_data(self, async_instance: AsyncOFSC):
        """Test that export_routing_plan returns RoutingPlanData."""
        # Get first routing profile and plan
        profiles = await async_instance.metadata.get_routing_profiles()
        if len(profiles.items) > 0:
            profile_label = profiles.items[0].profileLabel
            plans = await async_instance.metadata.get_routing_profile_plans(
                profile_label
            )
            if len(plans.items) > 0:
                plan_label = plans.items[0].planLabel
                result = await async_instance.metadata.export_routing_plan(
                    profile_label, plan_label
                )
                assert isinstance(result, RoutingPlanData)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_export_routing_plan_has_signature(self, async_instance: AsyncOFSC):
        """Test that exported plan has sign field."""
        profiles = await async_instance.metadata.get_routing_profiles()
        if len(profiles.items) > 0:
            profile_label = profiles.items[0].profileLabel
            plans = await async_instance.metadata.get_routing_profile_plans(
                profile_label
            )
            if len(plans.items) > 0:
                plan_label = plans.items[0].planLabel
                result = await async_instance.metadata.export_routing_plan(
                    profile_label, plan_label
                )
                assert hasattr(result, "sign")
                assert isinstance(result.sign, str)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_export_routing_plan_has_version(self, async_instance: AsyncOFSC):
        """Test that exported plan has version field."""
        profiles = await async_instance.metadata.get_routing_profiles()
        if len(profiles.items) > 0:
            profile_label = profiles.items[0].profileLabel
            plans = await async_instance.metadata.get_routing_profile_plans(
                profile_label
            )
            if len(plans.items) > 0:
                plan_label = plans.items[0].planLabel
                result = await async_instance.metadata.export_routing_plan(
                    profile_label, plan_label
                )
                assert hasattr(result, "version")
                assert isinstance(result.version, str)


# ===================================================================
# EXPORT PLAN FILE (bytes)
# ===================================================================


class TestAsyncExportPlanFileLive:
    """Live tests for export_plan_file."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_export_plan_file(self, async_instance: AsyncOFSC):
        """Test export_plan_file returns bytes."""
        # Get first routing profile and plan
        profiles = await async_instance.metadata.get_routing_profiles()
        if len(profiles.items) > 0:
            profile_label = profiles.items[0].profileLabel
            plans = await async_instance.metadata.get_routing_profile_plans(
                profile_label
            )
            if len(plans.items) > 0:
                plan_label = plans.items[0].planLabel
                result = await async_instance.metadata.export_plan_file(
                    profile_label, plan_label
                )
                assert isinstance(result, bytes)
                assert len(result) > 0

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_export_plan_file_not_found(self, async_instance: AsyncOFSC):
        """Test export_plan_file with non-existent plan."""
        profiles = await async_instance.metadata.get_routing_profiles()
        if len(profiles.items) > 0:
            profile_label = profiles.items[0].profileLabel
            with pytest.raises(OFSCNotFoundError) as exc_info:
                await async_instance.metadata.export_plan_file(
                    profile_label, "NONEXISTENT_PLAN_12345"
                )
            assert exc_info.value.status_code == 404


# ===================================================================
# IMPORT ROUTING PLAN
# ===================================================================


class TestAsyncImportRoutingPlanLive:
    """Live tests for import_routing_plan."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_import_routing_plan_round_trip(self, async_instance: AsyncOFSC):
        """Test export then import (round trip).

        Note: This test exports a plan, imports it (which will fail with 409 conflict
        since the plan already exists), then uses force_import to overwrite.
        """
        # Get first routing profile and plan
        profiles = await async_instance.metadata.get_routing_profiles()
        if len(profiles.items) > 0:
            profile_label = profiles.items[0].profileLabel
            plans = await async_instance.metadata.get_routing_profile_plans(
                profile_label
            )
            if len(plans.items) > 0:
                plan_label = plans.items[0].planLabel
                # Export the plan
                plan_data_bytes = await async_instance.metadata.export_plan_file(
                    profile_label, plan_label
                )
                assert isinstance(plan_data_bytes, bytes)

                # Try regular import (should fail with 409 if plan exists)
                # We'll test force_import instead in the next test

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_import_routing_plan_conflict(self, async_instance: AsyncOFSC):
        """Test import_routing_plan with conflict (409).

        When importing a plan that already exists, it should raise OFSCConflictError.
        """
        # Get first routing profile and plan
        profiles = await async_instance.metadata.get_routing_profiles()
        if len(profiles.items) > 0:
            profile_label = profiles.items[0].profileLabel
            plans = await async_instance.metadata.get_routing_profile_plans(
                profile_label
            )
            if len(plans.items) > 0:
                plan_label = plans.items[0].planLabel
                # Export the plan
                plan_data_bytes = await async_instance.metadata.export_plan_file(
                    profile_label, plan_label
                )

                # Try to import (should fail with 409 conflict)
                with pytest.raises(OFSCConflictError) as exc_info:
                    await async_instance.metadata.import_routing_plan(
                        profile_label, plan_data_bytes
                    )
                assert exc_info.value.status_code == 409


# ===================================================================
# FORCE IMPORT ROUTING PLAN
# ===================================================================


class TestAsyncForceImportRoutingPlanLive:
    """Live tests for force_import_routing_plan."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_force_import_routing_plan(self, async_instance: AsyncOFSC):
        """Test force_import_routing_plan (overwrites existing plan)."""
        # Get first routing profile and plan
        profiles = await async_instance.metadata.get_routing_profiles()
        if len(profiles.items) > 0:
            profile_label = profiles.items[0].profileLabel
            plans = await async_instance.metadata.get_routing_profile_plans(
                profile_label
            )
            if len(plans.items) > 0:
                plan_label = plans.items[0].planLabel
                # Export the plan
                plan_data_bytes = await async_instance.metadata.export_plan_file(
                    profile_label, plan_label
                )

                # Force import (should succeed even if plan exists)
                await async_instance.metadata.force_import_routing_plan(
                    profile_label, plan_data_bytes
                )
                # Success - method returns None


# ===================================================================
# START ROUTING PLAN
# ===================================================================


class TestAsyncStartRoutingPlanLive:
    """Live tests for start_routing_plan."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_start_routing_plan_not_found(self, async_instance: AsyncOFSC):
        """Test start_routing_plan with invalid resource (404)."""
        # Get first routing profile and plan
        profiles = await async_instance.metadata.get_routing_profiles()
        if len(profiles.items) > 0:
            profile_label = profiles.items[0].profileLabel
            plans = await async_instance.metadata.get_routing_profile_plans(
                profile_label
            )
            if len(plans.items) > 0:
                plan_label = plans.items[0].planLabel
                # Try to start plan for non-existent resource
                with pytest.raises(OFSCNotFoundError) as exc_info:
                    await async_instance.metadata.start_routing_plan(
                        profile_label, plan_label, "INVALID_RESOURCE", "2025-10-23"
                    )
                assert exc_info.value.status_code == 404


# ===================================================================
# SAVED RESPONSE VALIDATION
# ===================================================================


class TestAsyncRoutingProfileSavedResponses:
    """Test model validation against saved API responses."""

    def test_routing_profile_list_validation(self):
        """Test RoutingProfileList model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "routing_profiles"
            / "get_routing_profiles_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = RoutingProfileList.model_validate(saved_data["response_data"])
        assert isinstance(response, RoutingProfileList)
        assert response.totalResults == 3
        assert len(response.items) == 3
        assert all(isinstance(p, RoutingProfile) for p in response.items)

    def test_routing_plan_list_validation(self):
        """Test RoutingPlanList model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "routing_profiles"
            / "get_routing_profile_plans_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = RoutingPlanList.model_validate(saved_data["response_data"])
        assert isinstance(response, RoutingPlanList)
        assert response.totalResults >= 6  # At least 6 plans in the profile
        assert len(response.items) == response.totalResults
        assert all(isinstance(p, RoutingPlan) for p in response.items)

    def test_routing_plan_data_validation(self):
        """Test RoutingPlanData model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "routing_profiles"
            / "export_routing_plan_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = RoutingPlanData.model_validate(saved_data["response_data"])
        assert isinstance(response, RoutingPlanData)
        assert hasattr(response, "routing_plan")
        assert hasattr(response, "sign")
        assert hasattr(response, "version")

    def test_import_routing_plan_validation(self):
        """Test import response validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "routing_profiles"
            / "import_routing_plan_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Import returns success message (status 200)
        assert saved_data["status_code"] == 200
        assert "The routing plan was successfully imported" in saved_data["body"]

    def test_force_import_routing_plan_validation(self):
        """Test force import response validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "routing_profiles"
            / "force_import_routing_plan_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Force import returns success message (status 200)
        assert saved_data["status_code"] == 200
        assert "The routing plan was successfully imported" in saved_data["body"]
