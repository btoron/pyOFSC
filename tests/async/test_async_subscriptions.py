"""Tests for async subscription and event operations."""

import asyncio
import json
from pathlib import Path

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import (
    CreateSubscriptionRequest,
    EventListResponse,
    Subscription,
    SubscriptionListResponse,
)


# ===================================================================
# GET SUBSCRIPTIONS
# ===================================================================


class TestAsyncGetSubscriptionsLive:
    """Live tests for get_subscriptions."""

    @pytest.mark.serial
    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_subscriptions(self, async_instance: AsyncOFSC):
        """Test get_subscriptions with actual API."""
        result = await async_instance.core.get_subscriptions()

        assert isinstance(result, SubscriptionListResponse)
        assert hasattr(result, "items")
        assert hasattr(result, "totalResults")


# ===================================================================
# CREATE/DELETE SUBSCRIPTION
# ===================================================================


class TestAsyncCreateDeleteSubscriptionLive:
    """Live tests for create and delete subscription."""

    @pytest.mark.serial
    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_create_delete_subscription(self, async_instance: AsyncOFSC):
        """Test creating and deleting a subscription."""
        # Create subscription
        subscription_request = CreateSubscriptionRequest(
            events=["activityMoved"], title="Test Async Subscription"
        )

        created = await async_instance.core.create_subscription(subscription_request)

        assert isinstance(created, Subscription)
        assert hasattr(created, "subscriptionId")
        assert created.subscriptionId is not None

        subscription_id = created.subscriptionId

        # Get subscription details to verify it was created correctly
        details = await async_instance.core.get_subscription(subscription_id)

        assert isinstance(details, Subscription)
        assert details.subscriptionId == subscription_id
        # Note: API may not return title and events in all responses
        # Just verify we got the subscription details

        # Delete subscription
        await async_instance.core.delete_subscription(subscription_id)

        # Verify it's deleted - should raise 404
        with pytest.raises(OFSCNotFoundError):
            await async_instance.core.get_subscription(subscription_id)


# ===================================================================
# GET SUBSCRIPTION
# ===================================================================


class TestAsyncGetSubscriptionLive:
    """Live tests for get_subscription."""

    @pytest.mark.serial
    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_subscription_not_found(self, async_instance: AsyncOFSC):
        """Test get_subscription with non-existent ID."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.core.get_subscription("NONEXISTENT_SUBSCRIPTION_12345")


# ===================================================================
# GET EVENTS (FULL WORKFLOW)
# ===================================================================


class TestAsyncGetEventsLive:
    """Live tests for get_events with full workflow."""

    @pytest.mark.serial
    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_events_workflow(self, async_instance: AsyncOFSC, demo_data):
        """Test full event workflow: create subscription, move activity, get events."""
        # Get move data from demo_data fixture
        move_data = demo_data.get("events")
        if not move_data:
            pytest.skip("No event demo data available")

        # Step 1: Create subscription
        subscription_request = CreateSubscriptionRequest(
            events=["activityMoved"], title="Test Event Subscription"
        )

        created = await async_instance.core.create_subscription(subscription_request)
        subscription_id = created.subscriptionId

        try:
            # Step 2: Get subscription details to verify it's active
            details = await async_instance.core.get_subscription(subscription_id)
            assert details.subscriptionId == subscription_id

            # Step 3: Move activity to trigger event
            # Use the sync client for move_activity since it's not implemented in async yet
            from ofsc import OFSC
            from ofsc.exceptions import OFSAPIException

            sync_instance = OFSC(
                clientID=async_instance._config.clientID,
                companyName=async_instance._config.companyName,
                secret=async_instance._config.secret,
            )

            try:
                move_request = {"setResource": {"resourceId": move_data["move_to"]}}
                sync_instance.core.move_activity(
                    move_data["move_id"], json.dumps(move_request)
                )

                # Step 4: Wait for event to be processed
                await asyncio.sleep(3)

                # Step 5: Get events for this subscription
                params = {"subscriptionId": subscription_id}
                events = await async_instance.core.get_events(params)

                assert isinstance(events, EventListResponse)
                assert hasattr(events, "items")

                # Move activity back to original position
                move_back_request = {
                    "setResource": {"resourceId": move_data["move_from"]}
                }
                sync_instance.core.move_activity(
                    move_data["move_id"], json.dumps(move_back_request)
                )

            except OFSAPIException as e:
                # Check if the error is about past date
                error_detail = getattr(e, "detail", str(e))
                if "past date" in error_detail:
                    # Activity is in the past, can't move it
                    # Still verify we can get events (even if empty)
                    params = {"subscriptionId": subscription_id}
                    events = await async_instance.core.get_events(params)
                    assert isinstance(events, EventListResponse)
                else:
                    raise

        finally:
            # Step 6: Clean up - delete subscription (may already be deleted by fixture)
            try:
                await async_instance.core.delete_subscription(subscription_id)
            except OFSCNotFoundError:
                # Subscription already deleted by clear_subscriptions fixture
                pass


# ===================================================================
# SAVED RESPONSE VALIDATION
# ===================================================================


class TestAsyncSubscriptionSavedResponses:
    """Test model validation against saved API responses."""

    def test_subscriptions_list_response_validation(self):
        """Test SubscriptionListResponse validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "subscriptions"
            / "get_subscriptions_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = SubscriptionListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, SubscriptionListResponse)
        assert hasattr(response, "items")
        assert hasattr(response, "totalResults")
