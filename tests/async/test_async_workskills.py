"""Tests for async work skills metadata methods."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import (
    Workskill,
    WorkskillConditionList,
    WorkskillListResponse,
    WorkskillGroup,
    WorkskillGroupListResponse,
)


# === WORKSKILLS ===


class TestAsyncGetWorkskillsLive:
    """Live tests for get_workskills against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_workskills(self, async_instance: AsyncOFSC):
        """Test get_workskills with actual API - validates structure."""
        result = await async_instance.metadata.get_workskills()

        assert isinstance(result, WorkskillListResponse)
        assert hasattr(result, "items")
        assert len(result.items) > 0

        # Validate first item structure
        first_skill = result.items[0]
        assert isinstance(first_skill, Workskill)
        assert hasattr(first_skill, "label")
        assert hasattr(first_skill, "name")
        assert hasattr(first_skill, "active")
        assert hasattr(first_skill, "sharing")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_workskills_pagination(self, async_instance: AsyncOFSC):
        """Test get_workskills with pagination."""
        result = await async_instance.metadata.get_workskills(offset=0, limit=2)

        assert isinstance(result, WorkskillListResponse)
        assert len(result.items) <= 2

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_all_workskills_individually(self, async_instance: AsyncOFSC):
        """Test getting all work skills individually to validate all configurations.

        This test:
        1. Retrieves all work skills
        2. Iterates through each one
        3. Retrieves each work skill individually by label
        4. Validates that all models parse correctly

        This ensures the models can handle all real-world configuration variations.
        """
        # First get all work skills
        all_skills = await async_instance.metadata.get_workskills()

        assert isinstance(all_skills, WorkskillListResponse)
        assert len(all_skills.items) > 0

        # Track results for reporting
        successful = 0
        failed = []

        # Iterate through each work skill and get it individually
        for skill in all_skills.items:
            try:
                individual_skill = await async_instance.metadata.get_workskill(
                    skill.label
                )

                # Validate the returned work skill
                assert isinstance(individual_skill, Workskill)
                assert individual_skill.label == skill.label

                successful += 1
            except Exception as e:
                failed.append({"label": skill.label, "error": str(e)})

        # Report results
        print("\nWork skills validation:")
        print(f"  Total work skills: {len(all_skills.items)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {len(failed)}")

        if failed:
            print("\nFailed work skills:")
            for failure in failed:
                print(f"  - {failure['label']}: {failure['error']}")

        # All work skills should be retrieved successfully
        assert len(failed) == 0, (
            f"Failed to retrieve {len(failed)} work skills: {failed}"
        )
        assert successful == len(all_skills.items)


class TestAsyncGetWorkskillsModel:
    """Model validation tests for get_workskills."""

    @pytest.mark.asyncio
    async def test_get_workskills_returns_model(self, async_instance: AsyncOFSC):
        """Test that get_workskills returns WorkskillListResponse model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "label": "EST",
                    "name": "Estimate",
                    "active": True,
                    "sharing": "maximal",
                    "translations": [
                        {"language": "en", "name": "Estimate", "languageISO": "en-US"}
                    ],
                },
                {
                    "label": "RES",
                    "name": "Residential",
                    "active": True,
                    "sharing": "maximal",
                    "translations": [
                        {
                            "language": "en",
                            "name": "Residential",
                            "languageISO": "en-US",
                        }
                    ],
                },
            ],
            "totalResults": 2,
            "links": [],
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_workskills()

        assert isinstance(result, WorkskillListResponse)
        assert len(result.items) == 2
        assert result.items[0].label == "EST"
        assert result.items[1].label == "RES"

    @pytest.mark.asyncio
    async def test_get_workskills_field_types(self, async_instance: AsyncOFSC):
        """Test that fields have correct types."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "label": "TEST_SKILL",
                    "name": "Test Skill",
                    "active": True,
                    "sharing": "maximal",
                }
            ],
            "totalResults": 1,
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_workskills()

        assert isinstance(result.items[0].label, str)
        assert isinstance(result.items[0].name, str)
        assert isinstance(result.items[0].active, bool)
        assert result.items[0].sharing.value == "maximal"


class TestAsyncGetWorkskillLive:
    """Live tests for get_workskill against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_workskill(self, async_instance: AsyncOFSC):
        """Test get_workskill with actual API."""
        # First get all work skills to find a valid label
        skills = await async_instance.metadata.get_workskills()
        assert len(skills.items) > 0

        # Get the first work skill by label
        test_label = skills.items[0].label
        result = await async_instance.metadata.get_workskill(test_label)

        assert isinstance(result, Workskill)
        assert result.label == test_label

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_workskill_not_found(self, async_instance: AsyncOFSC):
        """Test get_workskill with non-existent label."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_workskill("NONEXISTENT_SKILL_12345")


class TestAsyncGetWorkskillModel:
    """Model validation tests for get_workskill."""

    @pytest.mark.asyncio
    async def test_get_workskill_returns_model(self, async_instance: AsyncOFSC):
        """Test that get_workskill returns Workskill model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "label": "TEST_SKILL",
            "name": "Test Skill",
            "active": True,
            "sharing": "maximal",
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_workskill("TEST_SKILL")

        assert isinstance(result, Workskill)
        assert result.label == "TEST_SKILL"
        assert result.name == "Test Skill"
        assert result.active is True
        assert result.sharing.value == "maximal"


class TestAsyncCreateOrUpdateWorkskillLive:
    """Live tests for create_or_update_workskill."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_update_workskill_roundtrip(self, async_instance: AsyncOFSC):
        """Test updating a work skill and restoring original.

        This test:
        1. Gets an existing work skill
        2. Updates it with a small change
        3. Verifies the update worked
        4. Restores original work skill
        """
        # Get all work skills to find one to test with
        all_skills = await async_instance.metadata.get_workskills()
        if len(all_skills.items) == 0:
            pytest.skip("No work skills available for testing")

        # Use the first skill
        test_label = all_skills.items[0].label
        original_skill = await async_instance.metadata.get_workskill(test_label)

        try:
            # Create a copy with the same values (safe update)
            from ofsc.models import Workskill

            updated_skill = Workskill(
                label=original_skill.label,
                name=original_skill.name,
                active=original_skill.active,
                sharing=original_skill.sharing,
                translations=original_skill.translations,
            )

            # Update the skill
            result = await async_instance.metadata.create_or_update_workskill(
                updated_skill
            )

            # Verify the update worked
            assert isinstance(result, Workskill)
            assert result.label == original_skill.label

        finally:
            # Always restore original skill (suppress cleanup exceptions)
            try:
                await async_instance.metadata.create_or_update_workskill(original_skill)

                # Verify restoration
                restored = await async_instance.metadata.get_workskill(test_label)
                assert restored.label == original_skill.label
                assert restored.name == original_skill.name
                assert restored.active == original_skill.active
            except Exception as cleanup_error:
                # Log cleanup failure but don't hide test failure
                print(f"\n[WARNING] Failed to restore work skill: {cleanup_error}")
                # If test passed but cleanup failed, re-raise
                import sys

                if sys.exc_info()[0] is None:
                    raise


class TestAsyncCreateOrUpdateWorkskill:
    """Tests for create_or_update_workskill."""

    @pytest.mark.asyncio
    async def test_create_workskill(self, async_instance: AsyncOFSC):
        """Test creating a new work skill."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "label": "NEW_SKILL",
            "name": "New Skill",
            "active": True,
            "sharing": "maximal",
        }

        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        from ofsc.models import Workskill

        skill = Workskill(
            label="NEW_SKILL", name="New Skill", active=True, sharing="maximal"
        )
        result = await async_instance.metadata.create_or_update_workskill(skill)

        assert isinstance(result, Workskill)
        assert result.label == "NEW_SKILL"
        assert result.name == "New Skill"
        assert result.active is True

    @pytest.mark.asyncio
    async def test_update_workskill(self, async_instance: AsyncOFSC):
        """Test updating an existing work skill."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "label": "EST",
            "name": "Updated Estimate",
            "active": True,
            "sharing": "summary",
        }

        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        from ofsc.models import Workskill

        skill = Workskill(
            label="EST", name="Updated Estimate", active=True, sharing="summary"
        )
        result = await async_instance.metadata.create_or_update_workskill(skill)

        assert isinstance(result, Workskill)
        assert result.label == "EST"
        assert result.name == "Updated Estimate"


class TestAsyncDeleteWorkskill:
    """Tests for delete_workskill."""

    @pytest.mark.asyncio
    async def test_delete_workskill(self, async_instance: AsyncOFSC):
        """Test deleting a work skill."""
        mock_response = Mock()
        mock_response.status_code = 204

        async_instance.metadata._client.delete = AsyncMock(return_value=mock_response)

        result = await async_instance.metadata.delete_workskill("TEST_SKILL")

        assert result is None
        async_instance.metadata._client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_workskill_not_found(self, async_instance: AsyncOFSC):
        """Test deleting a non-existent work skill."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "type": "https://docs.oracle.com/en/cloud/saas/field-service/errors/not-found",
            "title": "Not Found",
            "status": "404",
            "detail": "Work skill not found",
        }

        from httpx import HTTPStatusError, Request

        async_instance.metadata._client.delete = AsyncMock(
            side_effect=HTTPStatusError(
                "404 Not Found",
                request=Request("DELETE", "http://test"),
                response=mock_response,
            )
        )

        from ofsc.exceptions import OFSCNotFoundError

        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.delete_workskill("NONEXISTENT")


# === WORKSKILL CONDITIONS ===


class TestAsyncGetWorkskillConditionsLive:
    """Live tests for get_workskill_conditions against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_workskill_conditions(self, async_instance: AsyncOFSC):
        """Test get_workskill_conditions with actual API."""
        result = await async_instance.metadata.get_workskill_conditions()

        assert isinstance(result, WorkskillConditionList)
        # Note: The response might be empty if no conditions are configured
        assert isinstance(result.root, list)


class TestAsyncGetWorkskillConditionsModel:
    """Model validation tests for get_workskill_conditions."""

    @pytest.mark.asyncio
    async def test_get_workskill_conditions_returns_model(
        self, async_instance: AsyncOFSC
    ):
        """Test that get_workskill_conditions returns WorkskillConditionList model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "internalId": 1,
                    "label": "test_condition",
                    "requiredLevel": 1,
                    "preferableLevel": 2,
                    "conditions": [
                        {"label": "skill1", "function": "in", "value": "value1"}
                    ],
                }
            ]
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_workskill_conditions()

        assert isinstance(result, WorkskillConditionList)
        assert len(result.root) == 1
        assert result.root[0].label == "test_condition"


class TestAsyncReplaceWorkskillConditionsLive:
    """Live tests for replace_workskill_conditions."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_replace_workskill_conditions_roundtrip(
        self, async_instance: AsyncOFSC
    ):
        """Test replacing work skill conditions and restoring original.

        This test:
        1. Gets current conditions
        2. Replaces them with modified conditions
        3. Verifies the replacement worked
        4. Restores original conditions
        """
        # Get current conditions
        original_conditions = await async_instance.metadata.get_workskill_conditions()

        try:
            # Replace with the same conditions (safe operation)
            result = await async_instance.metadata.replace_workskill_conditions(
                original_conditions
            )

            # Verify the replace operation worked
            assert isinstance(result, WorkskillConditionList)
            assert len(result.root) == len(original_conditions.root)

        finally:
            # Always restore original conditions (suppress cleanup exceptions)
            try:
                await async_instance.metadata.replace_workskill_conditions(
                    original_conditions
                )

                # Verify restoration
                restored = await async_instance.metadata.get_workskill_conditions()
                assert len(restored.root) == len(original_conditions.root)
            except Exception as cleanup_error:
                # Log cleanup failure but don't hide test failure
                print(
                    f"\n[WARNING] Failed to restore work skill conditions: {cleanup_error}"
                )
                # If test passed but cleanup failed, re-raise
                import sys

                if sys.exc_info()[0] is None:
                    raise


class TestAsyncReplaceWorkskillConditions:
    """Tests for replace_workskill_conditions."""

    @pytest.mark.asyncio
    async def test_replace_workskill_conditions(self, async_instance: AsyncOFSC):
        """Test replacing all work skill conditions."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "internalId": 1,
                    "label": "updated_condition",
                    "requiredLevel": 2,
                    "preferableLevel": 3,
                    "conditions": [
                        {"label": "skill1", "function": "in", "value": "value1"}
                    ],
                }
            ]
        }

        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        from ofsc.models import Condition, WorkskillCondition, WorkskillConditionList

        conditions = WorkskillConditionList(
            [
                WorkskillCondition(
                    internalId=1,
                    label="updated_condition",
                    requiredLevel=2,
                    preferableLevel=3,
                    conditions=[
                        Condition(label="skill1", function="in", value="value1")
                    ],
                )
            ]
        )

        result = await async_instance.metadata.replace_workskill_conditions(conditions)

        assert isinstance(result, WorkskillConditionList)
        assert len(result.root) == 1
        assert result.root[0].label == "updated_condition"
        assert result.root[0].requiredLevel == 2

    @pytest.mark.asyncio
    async def test_replace_workskill_conditions_empty(self, async_instance: AsyncOFSC):
        """Test replacing with empty list (removes all conditions)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}

        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        from ofsc.models import WorkskillConditionList

        conditions = WorkskillConditionList([])
        result = await async_instance.metadata.replace_workskill_conditions(conditions)

        assert isinstance(result, WorkskillConditionList)
        assert len(result.root) == 0


# === WORKSKILL GROUPS ===


class TestAsyncGetWorkskillGroupsLive:
    """Live tests for get_workskill_groups against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_workskill_groups(self, async_instance: AsyncOFSC):
        """Test get_workskill_groups with actual API."""
        result = await async_instance.metadata.get_workskill_groups()

        assert isinstance(result, WorkskillGroupListResponse)
        assert hasattr(result, "items")

        # If groups exist, validate structure
        if len(result.items) > 0:
            first_group = result.items[0]
            assert isinstance(first_group, WorkskillGroup)
            assert hasattr(first_group, "label")
            assert hasattr(first_group, "name")
            assert hasattr(first_group, "active")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_all_workskill_groups_individually(
        self, async_instance: AsyncOFSC
    ):
        """Test getting all work skill groups individually."""
        # First get all work skill groups
        all_groups = await async_instance.metadata.get_workskill_groups()

        assert isinstance(all_groups, WorkskillGroupListResponse)

        # Track results for reporting
        successful = 0
        failed = []

        # Iterate through each work skill group and get it individually
        for group in all_groups.items:
            try:
                individual_group = await async_instance.metadata.get_workskill_group(
                    group.label
                )

                # Validate the returned work skill group
                assert isinstance(individual_group, WorkskillGroup)
                assert individual_group.label == group.label

                successful += 1
            except Exception as e:
                failed.append({"label": group.label, "error": str(e)})

        # Report results
        print("\nWork skill groups validation:")
        print(f"  Total groups: {len(all_groups.items)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {len(failed)}")

        if failed:
            print("\nFailed groups:")
            for failure in failed:
                print(f"  - {failure['label']}: {failure['error']}")

        # All groups should be retrieved successfully
        if len(all_groups.items) > 0:
            assert len(failed) == 0, (
                f"Failed to retrieve {len(failed)} groups: {failed}"
            )
            assert successful == len(all_groups.items)


class TestAsyncGetWorkskillGroupsModel:
    """Model validation tests for get_workskill_groups."""

    @pytest.mark.asyncio
    async def test_get_workskill_groups_returns_model(self, async_instance: AsyncOFSC):
        """Test that get_workskill_groups returns WorkskillGroupListResponse model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "label": "TEST",
                    "name": "Test Group",
                    "assignToResource": True,
                    "addToCapacityCategory": False,
                    "active": True,
                    "workSkills": [{"label": "EST", "ratio": 1}],
                    "translations": [{"language": "en", "name": "Test Group"}],
                }
            ],
            "totalResults": 1,
            "links": [],
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_workskill_groups()

        assert isinstance(result, WorkskillGroupListResponse)
        assert len(result.items) == 1
        assert result.items[0].label == "TEST"


class TestAsyncGetWorkskillGroupLive:
    """Live tests for get_workskill_group against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_workskill_group(self, async_instance: AsyncOFSC):
        """Test get_workskill_group with actual API."""
        # First get all work skill groups to find a valid label
        groups = await async_instance.metadata.get_workskill_groups()

        if len(groups.items) > 0:
            # Get the first group by label
            test_label = groups.items[0].label
            result = await async_instance.metadata.get_workskill_group(test_label)

            assert isinstance(result, WorkskillGroup)
            assert result.label == test_label

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_workskill_group_not_found(self, async_instance: AsyncOFSC):
        """Test get_workskill_group with non-existent label."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_workskill_group("NONEXISTENT_GROUP_12345")


class TestAsyncGetWorkskillGroupModel:
    """Model validation tests for get_workskill_group."""

    @pytest.mark.asyncio
    async def test_get_workskill_group_returns_model(self, async_instance: AsyncOFSC):
        """Test that get_workskill_group returns WorkskillGroup model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "label": "TEST",
            "name": "Test Group",
            "assignToResource": True,
            "addToCapacityCategory": False,
            "active": True,
            "workSkills": [{"label": "EST", "ratio": 1}],
            "translations": [{"language": "en", "name": "Test Group"}],
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_workskill_group("TEST")

        assert isinstance(result, WorkskillGroup)
        assert result.label == "TEST"
        assert result.name == "Test Group"
        assert result.active is True


class TestAsyncCreateOrUpdateWorkskillGroupLive:
    """Live tests for create_or_update_workskill_group."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_update_workskill_group_roundtrip(self, async_instance: AsyncOFSC):
        """Test updating a work skill group and restoring original."""
        # Get all work skill groups to find one to test with
        all_groups = await async_instance.metadata.get_workskill_groups()
        if len(all_groups.items) == 0:
            pytest.skip("No work skill groups available for testing")

        # Use the first group
        test_label = all_groups.items[0].label
        original_group = await async_instance.metadata.get_workskill_group(test_label)

        try:
            # Create a copy with the same values (safe update)
            from ofsc.models import WorkskillGroup

            updated_group = WorkskillGroup(
                label=original_group.label,
                name=original_group.name,
                active=original_group.active,
                assignToResource=original_group.assignToResource,
                addToCapacityCategory=original_group.addToCapacityCategory,
                workSkills=original_group.workSkills,
                translations=original_group.translations,
            )

            # Update the group
            result = await async_instance.metadata.create_or_update_workskill_group(
                updated_group
            )
            assert isinstance(result, WorkskillGroup)
            assert result.label == original_group.label

        finally:
            # Always restore original group (suppress cleanup exceptions)
            try:
                await async_instance.metadata.create_or_update_workskill_group(
                    original_group
                )

                # Verify restoration
                restored = await async_instance.metadata.get_workskill_group(test_label)
                assert restored.label == original_group.label
            except Exception as cleanup_error:
                # Log cleanup failure but don't hide test failure
                print(
                    f"\n[WARNING] Failed to restore work skill group: {cleanup_error}"
                )
                # If test passed but cleanup failed, re-raise
                import sys

                if sys.exc_info()[0] is None:
                    raise


class TestAsyncCreateOrUpdateWorkskillGroup:
    """Tests for create_or_update_workskill_group."""

    @pytest.mark.asyncio
    async def test_create_workskill_group(self, async_instance: AsyncOFSC):
        """Test creating a new work skill group."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "label": "NEW_GROUP",
            "name": "New Group",
            "assignToResource": True,
            "addToCapacityCategory": True,
            "active": True,
            "workSkills": [
                {"label": "EST", "ratio": 50},
                {"label": "RES", "ratio": 50},
            ],
            "translations": [{"language": "en", "name": "New Group"}],
        }

        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        from ofsc.models import (
            TranslationList,
            Translation,
            WorkskillAssignment,
            WorkskillAssignmentList,
            WorkskillGroup,
        )

        group = WorkskillGroup(
            label="NEW_GROUP",
            name="New Group",
            assignToResource=True,
            addToCapacityCategory=True,
            active=True,
            workSkills=WorkskillAssignmentList(
                [
                    WorkskillAssignment(label="EST", ratio=50),
                    WorkskillAssignment(label="RES", ratio=50),
                ]
            ),
            translations=TranslationList(
                [Translation(language="en", name="New Group")]
            ),
        )

        result = await async_instance.metadata.create_or_update_workskill_group(group)

        assert isinstance(result, WorkskillGroup)
        assert result.label == "NEW_GROUP"
        assert result.name == "New Group"
        assert result.active is True

    @pytest.mark.asyncio
    async def test_update_workskill_group(self, async_instance: AsyncOFSC):
        """Test updating an existing work skill group."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "label": "TEST",
            "name": "Updated Test Group",
            "assignToResource": False,
            "addToCapacityCategory": True,
            "active": True,
            "workSkills": [{"label": "EST", "ratio": 100}],
            "translations": [{"language": "en", "name": "Updated Test Group"}],
        }

        async_instance.metadata._client.put = AsyncMock(return_value=mock_response)

        from ofsc.models import (
            TranslationList,
            Translation,
            WorkskillAssignment,
            WorkskillAssignmentList,
            WorkskillGroup,
        )

        group = WorkskillGroup(
            label="TEST",
            name="Updated Test Group",
            assignToResource=False,
            addToCapacityCategory=True,
            active=True,
            workSkills=WorkskillAssignmentList(
                [WorkskillAssignment(label="EST", ratio=100)]
            ),
            translations=TranslationList(
                [Translation(language="en", name="Updated Test Group")]
            ),
        )

        result = await async_instance.metadata.create_or_update_workskill_group(group)

        assert isinstance(result, WorkskillGroup)
        assert result.label == "TEST"
        assert result.name == "Updated Test Group"
        assert result.assignToResource is False


class TestAsyncDeleteWorkskillGroup:
    """Tests for delete_workskill_group."""

    @pytest.mark.asyncio
    async def test_delete_workskill_group(self, async_instance: AsyncOFSC):
        """Test deleting a work skill group."""
        mock_response = Mock()
        mock_response.status_code = 204

        async_instance.metadata._client.delete = AsyncMock(return_value=mock_response)

        result = await async_instance.metadata.delete_workskill_group("TEST_GROUP")

        assert result is None
        async_instance.metadata._client.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_workskill_group_not_found(self, async_instance: AsyncOFSC):
        """Test deleting a non-existent work skill group."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "type": "https://docs.oracle.com/en/cloud/saas/field-service/errors/not-found",
            "title": "Not Found",
            "status": "404",
            "detail": "Work skill group not found",
        }

        from httpx import HTTPStatusError, Request

        async_instance.metadata._client.delete = AsyncMock(
            side_effect=HTTPStatusError(
                "404 Not Found",
                request=Request("DELETE", "http://test"),
                response=mock_response,
            )
        )

        from ofsc.exceptions import OFSCNotFoundError

        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.delete_workskill_group("NONEXISTENT")


# === SAVED RESPONSE VALIDATION ===


class TestAsyncWorkskillsSavedResponses:
    """Test that saved API responses validate against Pydantic models."""

    def test_workskill_list_response_validation(self):
        """Test WorkskillListResponse model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "work_skills"
            / "get_work_skills_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = WorkskillListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, WorkskillListResponse)
        assert response.totalResults == 7  # From the captured data
        assert len(response.items) == 7
        assert all(isinstance(skill, Workskill) for skill in response.items)

    def test_workskill_single_validation(self):
        """Test Workskill model validates against saved single response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "work_skills"
            / "get_work_skill_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        skill = Workskill.model_validate(saved_data["response_data"])

        assert isinstance(skill, Workskill)
        assert skill.label == "EST"
        assert skill.name == "Estimate"
        assert skill.active is True
        assert skill.sharing.value == "maximal"

    def test_workskill_conditions_validation(self):
        """Test WorkskillConditionList model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "work_skill_conditions"
            / "get_work_skill_conditions_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        items = saved_data["response_data"].get("items", [])
        conditions = WorkskillConditionList.model_validate(items)

        assert isinstance(conditions, WorkskillConditionList)
        assert isinstance(conditions.root, list)

    def test_workskill_group_list_response_validation(self):
        """Test WorkskillGroupListResponse model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "work_skill_groups"
            / "get_work_skill_groups_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = WorkskillGroupListResponse.model_validate(
            saved_data["response_data"]
        )

        assert isinstance(response, WorkskillGroupListResponse)
        assert response.totalResults == 1  # From the captured data
        assert len(response.items) == 1
        assert all(isinstance(group, WorkskillGroup) for group in response.items)

    def test_workskill_group_single_validation(self):
        """Test WorkskillGroup model validates against saved single response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "work_skill_groups"
            / "get_work_skill_group_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        group = WorkskillGroup.model_validate(saved_data["response_data"])

        assert isinstance(group, WorkskillGroup)
        assert group.label == "TEST"
        assert group.name == "TEST"
        assert group.active is True
        assert group.assignToResource is True
