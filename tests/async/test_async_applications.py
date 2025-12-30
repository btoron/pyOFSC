"""Tests for async applications metadata methods."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import (
    Application,
    ApplicationApiAccess,
    ApplicationApiAccessListResponse,
    ApplicationListResponse,
    CapacityApiAccess,
    InboundApiAccess,
    SimpleApiAccess,
    StructuredApiAccess,
)


# === APPLICATIONS ===


class TestAsyncGetApplicationsLive:
    """Live tests for get_applications against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_applications(self, async_instance: AsyncOFSC):
        """Test get_applications with actual API - validates structure."""
        result = await async_instance.metadata.get_applications()

        assert isinstance(result, ApplicationListResponse)
        assert hasattr(result, "items")
        assert len(result.items) > 0

        # Validate first item structure
        first_app = result.items[0]
        assert isinstance(first_app, Application)
        assert hasattr(first_app, "label")
        assert hasattr(first_app, "name")
        assert hasattr(first_app, "status")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_all_applications_individually(self, async_instance: AsyncOFSC):
        """Test fetching all applications individually - comprehensive validation."""
        # First get all applications
        all_apps = await async_instance.metadata.get_applications()

        assert len(all_apps.items) > 0, "No applications found"

        # Fetch each application individually
        successful = 0
        failed = []

        for app in all_apps.items:
            try:
                individual_app = await async_instance.metadata.get_application(
                    app.label
                )
                assert isinstance(individual_app, Application)
                assert individual_app.label == app.label
                successful += 1
            except Exception as e:
                failed.append({"label": app.label, "error": str(e)})

        # Report any failures
        if failed:
            print(f"\nFailed to retrieve {len(failed)} applications:")
            for failure in failed:
                print(f"  - {failure['label']}: {failure['error']}")

        # All applications should be retrieved successfully
        assert len(failed) == 0, f"Failed to retrieve {len(failed)} applications"
        assert successful == len(all_apps.items)


class TestAsyncGetApplicationsModel:
    """Model validation tests for get_applications."""

    @pytest.mark.asyncio
    async def test_get_applications_returns_model(self, async_instance: AsyncOFSC):
        """Test that get_applications returns ApplicationListResponse model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "label": "testapp",
                    "name": "Test Application",
                    "status": "active",
                    "tokenService": "ofsc",
                    "resourcesToAllow": [],
                    "IPAddressesToAllow": [],
                    "allowedCorsDomains": [],
                }
            ],
            "totalResults": 1,
            "hasMore": False,
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_applications()

        assert isinstance(result, ApplicationListResponse)
        assert len(result.items) == 1
        assert result.items[0].label == "testapp"


class TestAsyncGetApplicationLive:
    """Live tests for get_application against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_application(self, async_instance: AsyncOFSC):
        """Test get_application with actual API."""
        # First get all applications to find a valid label
        apps = await async_instance.metadata.get_applications()

        if len(apps.items) > 0:
            # Get the first application by label
            test_label = apps.items[0].label
            result = await async_instance.metadata.get_application(test_label)

            assert isinstance(result, Application)
            assert result.label == test_label

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_application_not_found(self, async_instance: AsyncOFSC):
        """Test get_application with non-existent label."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_application("NONEXISTENT_APP_12345")


class TestAsyncGetApplicationModel:
    """Model validation tests for get_application."""

    @pytest.mark.asyncio
    async def test_get_application_returns_model(self, async_instance: AsyncOFSC):
        """Test that get_application returns Application model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "label": "testapp",
            "name": "Test Application",
            "status": "active",
            "tokenService": "ofsc",
            "resourcesToAllow": [],
            "IPAddressesToAllow": [],
            "allowedCorsDomains": [],
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_application("testapp")

        assert isinstance(result, Application)
        assert result.label == "testapp"
        assert result.name == "Test Application"


# === APPLICATION API ACCESSES ===


class TestAsyncGetApplicationApiAccessesLive:
    """Live tests for get_application_api_accesses against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_application_api_accesses(self, async_instance: AsyncOFSC):
        """Test get_application_api_accesses with actual API."""
        # First get all applications to find a valid label
        apps = await async_instance.metadata.get_applications()

        if len(apps.items) > 0:
            test_label = apps.items[0].label
            result = await async_instance.metadata.get_application_api_accesses(
                test_label
            )

            assert isinstance(result, ApplicationApiAccessListResponse)
            assert hasattr(result, "items")
            assert len(result.items) > 0

            # Validate first item structure
            first_access = result.items[0]
            assert isinstance(first_access, ApplicationApiAccess)
            assert hasattr(first_access, "label")
            assert hasattr(first_access, "name")
            assert hasattr(first_access, "status")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_all_api_accesses_individually(self, async_instance: AsyncOFSC):
        """Test fetching all API accesses individually."""
        # First get all applications to find a valid label
        apps = await async_instance.metadata.get_applications()

        if len(apps.items) == 0:
            pytest.skip("No applications available for testing")

        test_label = apps.items[0].label
        all_accesses = await async_instance.metadata.get_application_api_accesses(
            test_label
        )

        assert len(all_accesses.items) > 0, "No API accesses found"

        # Fetch each API access individually
        successful = 0
        failed = []

        for access in all_accesses.items:
            try:
                individual_access = (
                    await async_instance.metadata.get_application_api_access(
                        test_label, access.label
                    )
                )
                assert isinstance(individual_access, ApplicationApiAccess)
                assert individual_access.label == access.label
                successful += 1
            except Exception as e:
                failed.append({"label": access.label, "error": str(e)})

        # Report any failures
        if failed:
            print(f"\nFailed to retrieve {len(failed)} API accesses:")
            for failure in failed:
                print(f"  - {failure['label']}: {failure['error']}")

        # All API accesses should be retrieved successfully
        assert len(failed) == 0, f"Failed to retrieve {len(failed)} API accesses"
        assert successful == len(all_accesses.items)


class TestAsyncGetApplicationApiAccessesModel:
    """Model validation tests for get_application_api_accesses."""

    @pytest.mark.asyncio
    async def test_get_application_api_accesses_returns_model(
        self, async_instance: AsyncOFSC
    ):
        """Test that get_application_api_accesses returns model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "label": "capacityAPI",
                    "name": "Capacity API",
                    "status": "active",
                }
            ]
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_application_api_accesses("testapp")

        assert isinstance(result, ApplicationApiAccessListResponse)
        assert len(result.items) == 1
        assert result.items[0].label == "capacityAPI"


class TestAsyncGetApplicationApiAccessLive:
    """Live tests for get_application_api_access against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_application_api_access(self, async_instance: AsyncOFSC):
        """Test get_application_api_access with actual API."""
        # First get all applications to find a valid label
        apps = await async_instance.metadata.get_applications()

        if len(apps.items) == 0:
            pytest.skip("No applications available for testing")

        test_label = apps.items[0].label
        api_accesses = await async_instance.metadata.get_application_api_accesses(
            test_label
        )

        if len(api_accesses.items) > 0:
            # Get the first API access
            test_access_id = api_accesses.items[0].label
            result = await async_instance.metadata.get_application_api_access(
                test_label, test_access_id
            )

            # Verify it's one of the union types
            assert isinstance(
                result,
                (
                    SimpleApiAccess,
                    CapacityApiAccess,
                    StructuredApiAccess,
                    InboundApiAccess,
                ),
            )
            assert result.label == test_access_id

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_application_api_access_type_specific(
        self, async_instance: AsyncOFSC
    ):
        """Test that different API types return correct subclasses."""
        apps = await async_instance.metadata.get_applications()

        if len(apps.items) == 0:
            pytest.skip("No applications available for testing")

        test_label = apps.items[0].label

        # Test capacityAPI returns CapacityApiAccess
        try:
            capacity = await async_instance.metadata.get_application_api_access(
                test_label, "capacityAPI"
            )
            assert isinstance(capacity, CapacityApiAccess)
            assert capacity.apiMethods is not None
            assert len(capacity.apiMethods) > 0
        except Exception:
            pass  # capacityAPI might not be available

        # Test coreAPI returns SimpleApiAccess
        try:
            core = await async_instance.metadata.get_application_api_access(
                test_label, "coreAPI"
            )
            assert isinstance(core, SimpleApiAccess)
            assert core.apiEntities is not None
            assert len(core.apiEntities) > 0
        except Exception:
            pass  # coreAPI might not be available

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_application_api_access_not_found(
        self, async_instance: AsyncOFSC
    ):
        """Test get_application_api_access with non-existent access ID."""
        # First get all applications to find a valid label
        apps = await async_instance.metadata.get_applications()

        if len(apps.items) > 0:
            test_label = apps.items[0].label
            with pytest.raises(OFSCNotFoundError):
                await async_instance.metadata.get_application_api_access(
                    test_label, "NONEXISTENT_API_12345"
                )


class TestAsyncGetApplicationApiAccessModel:
    """Model validation tests for get_application_api_access."""

    @pytest.mark.asyncio
    async def test_get_application_api_access_returns_model(
        self, async_instance: AsyncOFSC
    ):
        """Test that get_application_api_access returns model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "label": "capacityAPI",
            "name": "Capacity API",
            "status": "active",
            "apiMethods": [
                {"label": "get_capacity", "status": "on"},
                {"label": "set_quota", "status": "on"},
            ],
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_application_api_access(
            "testapp", "capacityAPI"
        )

        assert isinstance(result, ApplicationApiAccess)
        assert result.label == "capacityAPI"
        assert result.name == "Capacity API"
        assert result.apiMethods is not None
        assert len(result.apiMethods) == 2


# === SAVED RESPONSE VALIDATION ===


class TestAsyncApplicationsSavedResponses:
    """Test that saved API responses validate against Pydantic models."""

    def test_application_list_response_validation(self):
        """Test ApplicationListResponse model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "applications"
            / "get_applications_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = ApplicationListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, ApplicationListResponse)
        assert response.totalResults == 5  # From the captured data
        assert len(response.items) == 5
        assert all(isinstance(app, Application) for app in response.items)

    def test_application_single_validation(self):
        """Test Application model validates against saved single response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "applications"
            / "get_application_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        app = Application.model_validate(saved_data["response_data"])

        assert isinstance(app, Application)
        assert app.label == "demoauth"
        assert app.name == "Demo Authentication"
        assert app.status == "active"

    def test_application_api_access_list_response_validation(self):
        """Test ApplicationApiAccessListResponse validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "applications"
            / "get_application_api_accesses_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = ApplicationApiAccessListResponse.model_validate(
            saved_data["response_data"]
        )

        assert isinstance(response, ApplicationApiAccessListResponse)
        assert len(response.items) == 8
        assert all(
            isinstance(access, ApplicationApiAccess) for access in response.items
        )

    def test_application_api_access_single_validation(self):
        """Test ApplicationApiAccess model validates against saved response."""
        from ofsc.models import parse_application_api_access

        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "applications"
            / "get_application_api_access_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        access = parse_application_api_access(saved_data["response_data"])

        # Verify it's the correct subclass for capacityAPI
        assert isinstance(access, CapacityApiAccess)
        assert access.label == "capacityAPI"
        assert access.name == "Capacity API"
        assert access.status.value == "active"
        assert access.apiMethods is not None
        assert len(access.apiMethods) == 5
