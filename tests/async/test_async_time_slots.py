"""Async tests for time slot operations."""

import json
from datetime import time
from pathlib import Path

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.models import TimeSlot, TimeSlotListResponse


class TestAsyncGetTimeSlotsLive:
    """Live tests against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_time_slots(self, async_instance: AsyncOFSC):
        """Test get_time_slots with actual API - validates structure"""
        time_slots = await async_instance.metadata.get_time_slots(offset=0, limit=100)

        # Verify type validation
        assert isinstance(time_slots, TimeSlotListResponse)
        assert time_slots.totalResults is not None
        assert time_slots.totalResults >= 0
        assert hasattr(time_slots, "items")
        assert isinstance(time_slots.items, list)

        # Verify at least one time slot exists
        if len(time_slots.items) > 0:
            assert isinstance(time_slots.items[0], TimeSlot)


class TestAsyncGetTimeSlots:
    """Test async get_time_slots method."""

    @pytest.mark.asyncio
    async def test_get_time_slots_with_model(self, async_instance: AsyncOFSC):
        """Test that get_time_slots returns TimeSlotListResponse model"""
        time_slots = await async_instance.metadata.get_time_slots(offset=0, limit=100)

        # Verify type validation
        assert isinstance(time_slots, TimeSlotListResponse)
        assert hasattr(time_slots, "items")
        assert hasattr(time_slots, "totalResults")
        assert isinstance(time_slots.items, list)

        # Verify items are TimeSlot instances
        if len(time_slots.items) > 0:
            assert isinstance(time_slots.items[0], TimeSlot)
            assert hasattr(time_slots.items[0], "label")
            assert hasattr(time_slots.items[0], "name")
            assert hasattr(time_slots.items[0], "active")
            assert hasattr(time_slots.items[0], "isAllDay")

    @pytest.mark.asyncio
    async def test_get_time_slots_pagination(self, async_instance: AsyncOFSC):
        """Test get_time_slots with pagination"""
        # Get first page
        page1 = await async_instance.metadata.get_time_slots(offset=0, limit=3)
        assert isinstance(page1, TimeSlotListResponse)
        assert len(page1.items) <= 3

        # Get second page if there are enough time slots
        if page1.totalResults > 3:
            page2 = await async_instance.metadata.get_time_slots(offset=3, limit=3)
            assert isinstance(page2, TimeSlotListResponse)
            # Pages should have different items
            if len(page1.items) > 0 and len(page2.items) > 0:
                assert page1.items[0].label != page2.items[0].label

    @pytest.mark.asyncio
    async def test_get_time_slots_total_results(self, async_instance: AsyncOFSC):
        """Test that totalResults is populated"""
        time_slots = await async_instance.metadata.get_time_slots(offset=0, limit=100)
        assert time_slots.totalResults is not None
        assert isinstance(time_slots.totalResults, int)
        assert time_slots.totalResults >= 0

    @pytest.mark.asyncio
    async def test_get_time_slots_field_types(self, async_instance: AsyncOFSC):
        """Test that time slot fields have correct types"""
        time_slots = await async_instance.metadata.get_time_slots(offset=0, limit=100)

        if len(time_slots.items) > 0:
            time_slot = time_slots.items[0]
            assert isinstance(time_slot.label, str)
            assert isinstance(time_slot.name, str)
            assert isinstance(time_slot.active, bool)
            assert isinstance(time_slot.isAllDay, bool)

            # timeStart and timeEnd are optional (not present for all-day slots)
            if not time_slot.isAllDay:
                # Non-all-day slots should have start and end times
                assert time_slot.timeStart is not None
                assert time_slot.timeEnd is not None
                assert isinstance(time_slot.timeStart, time)
                assert isinstance(time_slot.timeEnd, time)


class TestAsyncGetTimeSlot:
    """Test async get_time_slot method."""

    @pytest.mark.asyncio
    async def test_get_time_slot_not_implemented(self, async_instance: AsyncOFSC):
        """Test that get_time_slot raises NotImplementedError"""
        with pytest.raises(NotImplementedError) as exc_info:
            await async_instance.metadata.get_time_slot("08-10")

        # Verify the error message explains why
        assert "Oracle Field Service API does not support" in str(exc_info.value)
        assert "get_time_slots()" in str(exc_info.value)


class TestAsyncTimeSlotSavedResponses:
    """Test model validation against saved API responses."""

    def test_time_slot_list_response_validation(self):
        """Test TimeSlotListResponse model validates against saved response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "time_slots"
            / "get_time_slots_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        response = TimeSlotListResponse.model_validate(saved_data["response_data"])

        # Verify structure
        assert isinstance(response, TimeSlotListResponse)
        assert hasattr(response, "items")
        assert hasattr(response, "totalResults")
        assert len(response.items) > 0
        assert all(isinstance(item, TimeSlot) for item in response.items)

        # Verify first time slot details
        first_slot = response.items[0]
        assert isinstance(first_slot, TimeSlot)
        assert first_slot.label == "08-10"
        assert first_slot.name == "08-10"
        assert first_slot.active is True
        assert first_slot.isAllDay is False
        assert first_slot.timeStart == time(8, 0)
        assert first_slot.timeEnd == time(10, 0)

        # Verify all-day slot if present
        all_day_slots = [slot for slot in response.items if slot.isAllDay]
        if all_day_slots:
            all_day_slot = all_day_slots[0]
            assert all_day_slot.isAllDay is True
            # All-day slots may not have timeStart/timeEnd
            assert all_day_slot.label is not None
            assert all_day_slot.name is not None
