"""Tests for async capacity areas metadata methods."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import CapacityArea, CapacityAreaListResponse


# === GET CAPACITY AREAS (LIST) ===


class TestAsyncGetCapacityAreasLive:
    """Live tests for get_capacity_areas against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_areas(self, async_instance: AsyncOFSC):
        """Test get_capacity_areas with actual API - validates structure."""
        result = await async_instance.metadata.get_capacity_areas()

        assert isinstance(result, CapacityAreaListResponse)
        assert hasattr(result, "items")
        assert len(result.items) > 0

        # Validate first item structure
        first_area = result.items[0]
        assert isinstance(first_area, CapacityArea)
        assert hasattr(first_area, "label")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_areas_with_expand_parent(
        self, async_instance: AsyncOFSC
    ):
        """Test get_capacity_areas with expandParent=True."""
        result = await async_instance.metadata.get_capacity_areas(expandParent=True)

        assert isinstance(result, CapacityAreaListResponse)
        assert len(result.items) > 0

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_areas_with_fields(self, async_instance: AsyncOFSC):
        """Test get_capacity_areas with custom fields."""
        result = await async_instance.metadata.get_capacity_areas(
            fields=["label", "name", "status"]
        )

        assert isinstance(result, CapacityAreaListResponse)
        assert len(result.items) > 0

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_areas_active_only(self, async_instance: AsyncOFSC):
        """Test get_capacity_areas with activeOnly=True."""
        result = await async_instance.metadata.get_capacity_areas(activeOnly=True)

        assert isinstance(result, CapacityAreaListResponse)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_areas_areas_only(self, async_instance: AsyncOFSC):
        """Test get_capacity_areas with areasOnly=True."""
        result = await async_instance.metadata.get_capacity_areas(areasOnly=True)

        assert isinstance(result, CapacityAreaListResponse)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_all_capacity_areas_individually(self, async_instance: AsyncOFSC):
        """Test getting all capacity areas individually to validate all configurations.

        This test:
        1. Retrieves all capacity areas
        2. Iterates through each one
        3. Retrieves each area individually by label
        4. Validates that all models parse correctly

        This ensures the models can handle all real-world configuration variations.
        """
        # First get all capacity areas
        all_areas = await async_instance.metadata.get_capacity_areas()

        assert isinstance(all_areas, CapacityAreaListResponse)
        assert len(all_areas.items) > 0

        # Track results for reporting
        successful = 0
        failed = []

        # Iterate through each area and get it individually
        for area in all_areas.items:
            try:
                individual_area = await async_instance.metadata.get_capacity_area(
                    area.label
                )

                # Validate the returned area
                assert isinstance(individual_area, CapacityArea)
                assert individual_area.label == area.label

                successful += 1
            except Exception as e:
                failed.append({"label": area.label, "error": str(e)})

        # Report results
        print("\nCapacity Areas validation:")
        print(f"  Total areas: {len(all_areas.items)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {len(failed)}")

        if failed:
            print("\nFailed areas:")
            for failure in failed:
                print(f"  - {failure['label']}: {failure['error']}")

        # All areas should be retrieved successfully
        assert len(failed) == 0, f"Failed to retrieve {len(failed)} areas: {failed}"
        assert successful == len(all_areas.items)


class TestAsyncGetCapacityAreas:
    """Model validation tests for get_capacity_areas."""

    @pytest.mark.asyncio
    async def test_get_capacity_areas_with_model(self, async_instance: AsyncOFSC):
        """Test that get_capacity_areas returns CapacityAreaListResponse model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"label": "AREA1"},
                {"label": "AREA2"},
            ],
            "links": [],
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_capacity_areas()

        assert isinstance(result, CapacityAreaListResponse)
        assert len(result.items) == 2
        assert result.items[0].label == "AREA1"
        assert result.items[1].label == "AREA2"

    @pytest.mark.asyncio
    async def test_get_capacity_areas_field_types(self, async_instance: AsyncOFSC):
        """Test that fields have correct types."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"label": "TEST_AREA"}],
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_capacity_areas()

        assert isinstance(result.items[0].label, str)


# === GET CAPACITY AREA (SINGLE) ===


class TestAsyncGetCapacityAreaLive:
    """Live tests for get_capacity_area against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_area(self, async_instance: AsyncOFSC):
        """Test get_capacity_area with actual API."""
        # First get all areas to find a valid label
        areas = await async_instance.metadata.get_capacity_areas()
        assert len(areas.items) > 0

        # Get the first area by label
        test_label = areas.items[0].label
        result = await async_instance.metadata.get_capacity_area(test_label)

        assert isinstance(result, CapacityArea)
        assert result.label == test_label

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_area_not_found(self, async_instance: AsyncOFSC):
        """Test get_capacity_area with non-existent label."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_capacity_area("NONEXISTENT_AREA_12345")


class TestAsyncGetCapacityArea:
    """Model validation tests for get_capacity_area."""

    @pytest.mark.asyncio
    async def test_get_capacity_area_with_model(self, async_instance: AsyncOFSC):
        """Test that get_capacity_area returns CapacityArea model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "label": "TEST_AREA",
            "name": "Test Area",
            "status": "active",
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_capacity_area("TEST_AREA")

        assert isinstance(result, CapacityArea)
        assert result.label == "TEST_AREA"
        assert result.name == "Test Area"


# === SAVED RESPONSE VALIDATION ===


class TestAsyncCapacityAreasSavedResponses:
    """Test that saved API responses validate against Pydantic models."""

    def test_capacity_area_list_response_validation(self):
        """Test CapacityAreaListResponse model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "capacity_areas"
            / "get_capacity_areas_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = CapacityAreaListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, CapacityAreaListResponse)
        assert len(response.items) >= 5  # At least 5 areas in test data
        assert all(isinstance(area, CapacityArea) for area in response.items)

    def test_capacity_area_expanded_validation(self):
        """Test CapacityAreaListResponse with expanded parent validates."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "capacity_areas"
            / "get_capacity_areas_expanded_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = CapacityAreaListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, CapacityAreaListResponse)
        assert len(response.items) >= 5

    def test_capacity_area_single_validation(self):
        """Test CapacityArea model validates against saved single response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "capacity_areas"
            / "get_capacity_area_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        area = CapacityArea.model_validate(saved_data["response_data"])

        assert isinstance(area, CapacityArea)
        assert area.label == "FLUSA"
