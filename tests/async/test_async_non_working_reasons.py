"""Async tests for non-working reason operations."""

import json
from pathlib import Path

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.models import NonWorkingReason, NonWorkingReasonListResponse


class TestAsyncGetNonWorkingReasonsLive:
    """Live tests against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_non_working_reasons(self, async_instance: AsyncOFSC):
        """Test get_non_working_reasons with actual API - validates structure"""
        non_working_reasons = await async_instance.metadata.get_non_working_reasons(
            offset=0, limit=100
        )

        # Verify type validation
        assert isinstance(non_working_reasons, NonWorkingReasonListResponse)
        assert non_working_reasons.totalResults is not None
        assert non_working_reasons.totalResults >= 0
        assert hasattr(non_working_reasons, "items")
        assert isinstance(non_working_reasons.items, list)

        # Verify at least one non-working reason exists
        if len(non_working_reasons.items) > 0:
            assert isinstance(non_working_reasons.items[0], NonWorkingReason)


class TestAsyncGetNonWorkingReasons:
    """Test async get_non_working_reasons method."""

    @pytest.mark.asyncio
    async def test_get_non_working_reasons_with_model(self, async_instance: AsyncOFSC):
        """Test that get_non_working_reasons returns NonWorkingReasonListResponse model"""
        non_working_reasons = await async_instance.metadata.get_non_working_reasons(
            offset=0, limit=100
        )

        # Verify type validation
        assert isinstance(non_working_reasons, NonWorkingReasonListResponse)
        assert hasattr(non_working_reasons, "items")
        assert hasattr(non_working_reasons, "totalResults")
        assert isinstance(non_working_reasons.items, list)

        # Verify items are NonWorkingReason instances
        if len(non_working_reasons.items) > 0:
            assert isinstance(non_working_reasons.items[0], NonWorkingReason)
            assert hasattr(non_working_reasons.items[0], "label")
            assert hasattr(non_working_reasons.items[0], "name")
            assert hasattr(non_working_reasons.items[0], "active")

    @pytest.mark.asyncio
    async def test_get_non_working_reasons_pagination(self, async_instance: AsyncOFSC):
        """Test get_non_working_reasons with pagination"""
        # Get first page
        page1 = await async_instance.metadata.get_non_working_reasons(offset=0, limit=3)
        assert isinstance(page1, NonWorkingReasonListResponse)
        assert len(page1.items) <= 3

        # Get second page if there are enough non-working reasons
        if page1.totalResults > 3:
            page2 = await async_instance.metadata.get_non_working_reasons(
                offset=3, limit=3
            )
            assert isinstance(page2, NonWorkingReasonListResponse)
            # Pages should have different items
            if len(page1.items) > 0 and len(page2.items) > 0:
                assert page1.items[0].label != page2.items[0].label

    @pytest.mark.asyncio
    async def test_get_non_working_reasons_total_results(
        self, async_instance: AsyncOFSC
    ):
        """Test that totalResults is populated"""
        non_working_reasons = await async_instance.metadata.get_non_working_reasons(
            offset=0, limit=100
        )
        assert non_working_reasons.totalResults is not None
        assert isinstance(non_working_reasons.totalResults, int)
        assert non_working_reasons.totalResults >= 0

    @pytest.mark.asyncio
    async def test_get_non_working_reasons_field_types(self, async_instance: AsyncOFSC):
        """Test that non-working reason fields have correct types"""
        non_working_reasons = await async_instance.metadata.get_non_working_reasons(
            offset=0, limit=100
        )

        if len(non_working_reasons.items) > 0:
            reason = non_working_reasons.items[0]
            assert isinstance(reason.label, str)
            assert isinstance(reason.name, str)
            assert isinstance(reason.active, bool)


class TestAsyncGetNonWorkingReason:
    """Test async get_non_working_reason method."""

    @pytest.mark.asyncio
    async def test_get_non_working_reason_not_implemented(
        self, async_instance: AsyncOFSC
    ):
        """Test that get_non_working_reason raises NotImplementedError"""
        with pytest.raises(NotImplementedError) as exc_info:
            await async_instance.metadata.get_non_working_reason("ILLNESS")

        # Verify the error message explains why
        assert "Oracle Field Service API does not support" in str(exc_info.value)
        assert "get_non_working_reasons()" in str(exc_info.value)


class TestAsyncNonWorkingReasonSavedResponses:
    """Test model validation against saved API responses."""

    def test_non_working_reason_list_response_validation(self):
        """Test NonWorkingReasonListResponse model validates against saved response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "non_working_reasons"
            / "get_non_working_reasons_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        response = NonWorkingReasonListResponse.model_validate(
            saved_data["response_data"]
        )

        # Verify structure
        assert isinstance(response, NonWorkingReasonListResponse)
        assert hasattr(response, "items")
        assert hasattr(response, "totalResults")
        assert len(response.items) > 0
        assert all(isinstance(item, NonWorkingReason) for item in response.items)

        # Verify first non-working reason details
        first_reason = response.items[0]
        assert isinstance(first_reason, NonWorkingReason)
        assert first_reason.label == "ILLNESS"
        assert first_reason.name == "Illness"
        assert first_reason.active is True
