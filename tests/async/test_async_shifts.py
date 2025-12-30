"""Tests for async shifts metadata methods."""

import json
from datetime import time
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import Shift, ShiftListResponse


# === GET SHIFTS (LIST) ===


class TestAsyncGetShiftsLive:
    """Live tests for get_shifts against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_shifts(self, async_instance: AsyncOFSC):
        """Test get_shifts with actual API - validates structure."""
        result = await async_instance.metadata.get_shifts()

        assert isinstance(result, ShiftListResponse)
        assert hasattr(result, "items")
        assert len(result.items) > 0

        # Validate first item structure
        first_shift = result.items[0]
        assert isinstance(first_shift, Shift)
        assert hasattr(first_shift, "label")
        assert hasattr(first_shift, "name")
        assert hasattr(first_shift, "active")
        assert hasattr(first_shift, "type")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_shifts_pagination(self, async_instance: AsyncOFSC):
        """Test get_shifts with pagination."""
        result = await async_instance.metadata.get_shifts(offset=0, limit=2)

        assert isinstance(result, ShiftListResponse)
        assert len(result.items) <= 2

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_all_shifts_individually(self, async_instance: AsyncOFSC):
        """Test getting all shifts individually to validate all configurations.

        This test:
        1. Retrieves all shifts
        2. Iterates through each one
        3. Retrieves each shift individually by label
        4. Validates that all models parse correctly

        This ensures the models can handle all real-world configuration variations.
        """
        # First get all shifts
        all_shifts = await async_instance.metadata.get_shifts()

        assert isinstance(all_shifts, ShiftListResponse)
        assert len(all_shifts.items) > 0

        # Track results for reporting
        successful = 0
        failed = []

        # Iterate through each shift and get it individually
        for shift in all_shifts.items:
            try:
                individual_shift = await async_instance.metadata.get_shift(shift.label)

                # Validate the returned shift
                assert isinstance(individual_shift, Shift)
                assert individual_shift.label == shift.label

                successful += 1
            except Exception as e:
                failed.append({"label": shift.label, "error": str(e)})

        # Report results
        print("\nShifts validation:")
        print(f"  Total shifts: {len(all_shifts.items)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {len(failed)}")

        if failed:
            print("\nFailed shifts:")
            for failure in failed:
                print(f"  - {failure['label']}: {failure['error']}")

        # All shifts should be retrieved successfully
        assert len(failed) == 0, f"Failed to retrieve {len(failed)} shifts: {failed}"
        assert successful == len(all_shifts.items)


class TestAsyncGetShiftsModel:
    """Model validation tests for get_shifts."""

    @pytest.mark.asyncio
    async def test_get_shifts_returns_model(self, async_instance: AsyncOFSC):
        """Test that get_shifts returns ShiftListResponse model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "label": "8-17",
                    "name": "First shift 8-17",
                    "active": True,
                    "type": "regular",
                    "workTimeStart": "08:00:00",
                    "workTimeEnd": "17:00:00",
                    "points": 100,
                },
                {
                    "label": "on-call",
                    "name": "On-call",
                    "active": True,
                    "type": "on-call",
                    "workTimeStart": "18:00:00",
                    "workTimeEnd": "23:00:00",
                    "decoration": "yellow",
                },
            ],
            "totalResults": 2,
            "links": [],
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_shifts()

        assert isinstance(result, ShiftListResponse)
        assert len(result.items) == 2
        assert result.items[0].label == "8-17"
        assert result.items[1].label == "on-call"

    @pytest.mark.asyncio
    async def test_get_shifts_field_types(self, async_instance: AsyncOFSC):
        """Test that fields have correct types."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "label": "TEST_SHIFT",
                    "name": "Test Shift",
                    "active": True,
                    "type": "regular",
                    "workTimeStart": "08:00:00",
                    "workTimeEnd": "17:00:00",
                    "points": 100,
                }
            ],
            "totalResults": 1,
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_shifts()

        assert isinstance(result.items[0].label, str)
        assert isinstance(result.items[0].name, str)
        assert isinstance(result.items[0].active, bool)
        assert result.items[0].type.value == "regular"


# === GET SHIFT (SINGLE) ===


class TestAsyncGetShiftLive:
    """Live tests for get_shift against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_shift(self, async_instance: AsyncOFSC):
        """Test get_shift with actual API."""
        # First get all shifts to find a valid label
        shifts = await async_instance.metadata.get_shifts()
        assert len(shifts.items) > 0

        # Get the first shift by label
        test_label = shifts.items[0].label
        result = await async_instance.metadata.get_shift(test_label)

        assert isinstance(result, Shift)
        assert result.label == test_label

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_shift_not_found(self, async_instance: AsyncOFSC):
        """Test get_shift with non-existent label."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_shift("NONEXISTENT_SHIFT_12345")


class TestAsyncGetShiftModel:
    """Model validation tests for get_shift."""

    @pytest.mark.asyncio
    async def test_get_shift_returns_model(self, async_instance: AsyncOFSC):
        """Test that get_shift returns Shift model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "label": "TEST_SHIFT",
            "name": "Test Shift",
            "active": True,
            "type": "regular",
            "workTimeStart": "08:00:00",
            "workTimeEnd": "17:00:00",
            "points": 100,
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_shift("TEST_SHIFT")

        assert isinstance(result, Shift)
        assert result.label == "TEST_SHIFT"
        assert result.name == "Test Shift"
        assert result.active is True
        assert result.type.value == "regular"


# === SAVED RESPONSE VALIDATION ===


class TestAsyncShiftsSavedResponses:
    """Test that saved API responses validate against Pydantic models."""

    def test_shift_list_response_validation(self):
        """Test ShiftListResponse model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "shifts"
            / "get_shifts_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = ShiftListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, ShiftListResponse)
        assert response.totalResults == 12  # From the captured data
        assert len(response.items) == 12
        assert all(isinstance(shift, Shift) for shift in response.items)

    def test_shift_single_validation(self):
        """Test Shift model validates against saved single response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "shifts"
            / "get_shift_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        shift = Shift.model_validate(saved_data["response_data"])

        assert isinstance(shift, Shift)
        assert shift.label == "8-17"
        assert shift.name == "First shift 8-17"
        assert shift.active is True
        assert shift.type.value == "regular"
        assert shift.workTimeStart == time(8, 0, 0)
        assert shift.workTimeEnd == time(17, 0, 0)
        assert shift.points == 100
