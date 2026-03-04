"""Async tests for resource write/delete operations."""

from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from ofsc.async_client import AsyncOFSC
import pydantic
from ofsc.exceptions import (
    OFSCAuthenticationError,
    OFSCConflictError,
    OFSCNetworkError,
    OFSCNotFoundError,
)
from ofsc.models import (
    AssignedLocationsResponse,
    Inventory,
    Location,
    Resource,
    ResourceCreate,
    ResourceUsersListResponse,
    ResourceWorkScheduleResponse,
    ResourceWorkskillListResponse,
    ResourceWorkzoneListResponse,
)


def _make_http_error(status_code: int, detail: str = "Error") -> httpx.HTTPStatusError:
    """Helper: build a fake httpx.HTTPStatusError."""
    mock_request = Mock()
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = {
        "type": "https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html",
        "title": "Error",
        "detail": detail,
    }
    mock_response.text = detail
    http_error = httpx.HTTPStatusError(
        f"{status_code} Error", request=mock_request, response=mock_response
    )
    mock_response.raise_for_status = Mock(side_effect=http_error)
    return http_error


def _resource_payload() -> dict:
    return {
        "resourceId": "TEST_RES_001",
        "parentResourceId": "PARENT_BUCKET",
        "resourceType": "BK",
        "name": "Test Resource",
        "status": "active",
        "organization": "default",
        "language": "en",
        "timeZone": "US/Eastern",
    }


# ---------------------------------------------------------------------------
# create_resource
# ---------------------------------------------------------------------------


class TestAsyncCreateResource:
    """Mocked tests for create_resource."""

    @pytest.mark.asyncio
    async def test_create_resource_returns_resource(self, mock_instance: AsyncOFSC):
        """Test create_resource returns Resource model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = _resource_payload()
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.put = AsyncMock(return_value=mock_response)

        result = await mock_instance.core.create_resource(
            "TEST_RES_001", _resource_payload()
        )

        assert isinstance(result, Resource)
        assert result.resourceId == "TEST_RES_001"
        assert result.name == "Test Resource"

    @pytest.mark.asyncio
    async def test_create_resource_accepts_model(self, mock_instance: AsyncOFSC):
        """Test create_resource accepts a Resource model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = _resource_payload()
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.put = AsyncMock(return_value=mock_response)

        resource_model = Resource.model_validate(_resource_payload())
        result = await mock_instance.core.create_resource(
            "TEST_RES_001", resource_model
        )

        assert isinstance(result, Resource)
        call_kwargs = mock_instance.core._client.put.call_args
        assert "json" in call_kwargs.kwargs

    @pytest.mark.asyncio
    async def test_create_resource_uses_put(self, mock_instance: AsyncOFSC):
        """Test create_resource uses PUT method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = _resource_payload()
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.put = AsyncMock(return_value=mock_response)

        await mock_instance.core.create_resource("TEST_RES_001", _resource_payload())

        assert mock_instance.core._client.put.called
        call_args = mock_instance.core._client.put.call_args
        assert "TEST_RES_001" in call_args.args[0]


# ---------------------------------------------------------------------------
# create_resource_from_obj
# ---------------------------------------------------------------------------


class TestAsyncCreateResourceFromObj:
    """Mocked tests for create_resource_from_obj."""

    @pytest.mark.asyncio
    async def test_create_resource_from_obj_returns_resource(
        self, async_instance: AsyncOFSC
    ):
        """Test create_resource_from_obj returns Resource model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = _resource_payload()
        mock_response.raise_for_status = Mock()
        async_instance.core._client.put = AsyncMock(return_value=mock_response)

        result = await async_instance.core.create_resource_from_obj(
            "TEST_RES_001", _resource_payload()
        )

        assert isinstance(result, Resource)

    @pytest.mark.asyncio
    async def test_create_resource_from_obj_sends_json(self, mock_instance: AsyncOFSC):
        """Test create_resource_from_obj sends dict as JSON body."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = _resource_payload()
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.put = AsyncMock(return_value=mock_response)

        data = _resource_payload()
        await mock_instance.core.create_resource_from_obj("TEST_RES_001", data)

        call_kwargs = mock_instance.core._client.put.call_args
        assert call_kwargs.kwargs["json"] == data


# ---------------------------------------------------------------------------
# update_resource
# ---------------------------------------------------------------------------


class TestAsyncUpdateResource:
    """Mocked tests for update_resource."""

    @pytest.mark.asyncio
    async def test_update_resource_returns_resource(self, mock_instance: AsyncOFSC):
        """Test update_resource returns Resource model."""
        updated_payload = {**_resource_payload(), "name": "Updated Name"}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = updated_payload
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.patch = AsyncMock(return_value=mock_response)

        result = await mock_instance.core.update_resource(
            "TEST_RES_001", {"name": "Updated Name"}
        )

        assert isinstance(result, Resource)
        assert result.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_resource_uses_patch(self, mock_instance: AsyncOFSC):
        """Test update_resource uses PATCH method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = _resource_payload()
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.patch = AsyncMock(return_value=mock_response)

        await mock_instance.core.update_resource("TEST_RES_001", {"name": "X"})

        assert mock_instance.core._client.patch.called

    @pytest.mark.asyncio
    async def test_update_resource_identify_by_internal_id(
        self, async_instance: AsyncOFSC
    ):
        """Test update_resource passes identifyResourceBy param when flag is set."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = _resource_payload()
        mock_response.raise_for_status = Mock()
        async_instance.core._client.patch = AsyncMock(return_value=mock_response)

        await async_instance.core.update_resource(
            "12345", {"name": "X"}, identify_by_internal_id=True
        )

        call_kwargs = async_instance.core._client.patch.call_args
        assert call_kwargs.kwargs.get("params") == {
            "identifyResourceBy": "resourceInternalId"
        }


# ---------------------------------------------------------------------------
# set_resource_users / delete_resource_users
# ---------------------------------------------------------------------------


class TestAsyncSetDeleteResourceUsers:
    """Mocked tests for set_resource_users and delete_resource_users."""

    @pytest.mark.asyncio
    async def test_set_resource_users_returns_list_response(
        self, async_instance: AsyncOFSC
    ):
        """Test set_resource_users returns ResourceUsersListResponse."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"login": "user1"}, {"login": "user2"}],
            "totalResults": 2,
        }
        mock_response.raise_for_status = Mock()
        async_instance.core._client.put = AsyncMock(return_value=mock_response)

        result = await async_instance.core.set_resource_users(
            resource_id="TEST_RES_001", users=["user1", "user2"]
        )

        assert isinstance(result, ResourceUsersListResponse)
        assert len(result.items) == 2

    @pytest.mark.asyncio
    async def test_set_resource_users_body_format(self, mock_instance: AsyncOFSC):
        """Test set_resource_users sends correct body format."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [], "totalResults": 0}
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.put = AsyncMock(return_value=mock_response)

        await mock_instance.core.set_resource_users(
            resource_id="RES1", users=["alice", "bob"]
        )

        call_kwargs = mock_instance.core._client.put.call_args
        assert call_kwargs.kwargs["json"] == {
            "items": [{"login": "alice"}, {"login": "bob"}]
        }

    @pytest.mark.asyncio
    async def test_delete_resource_users_returns_none(self, mock_instance: AsyncOFSC):
        """Test delete_resource_users returns None on 204."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.delete = AsyncMock(return_value=mock_response)

        result = await mock_instance.core.delete_resource_users("TEST_RES_001")

        assert result is None
        assert mock_instance.core._client.delete.called
        url = mock_instance.core._client.delete.call_args.args[0]
        assert "users" in url


# ---------------------------------------------------------------------------
# set_resource_workschedules
# ---------------------------------------------------------------------------


class TestAsyncSetResourceWorkschedules:
    """Mocked tests for set_resource_workschedules."""

    @pytest.mark.asyncio
    async def test_set_resource_workschedules_returns_response(
        self, async_instance: AsyncOFSC
    ):
        """Test set_resource_workschedules returns ResourceWorkScheduleResponse."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [],
            "totalResults": 0,
        }
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        result = await async_instance.core.set_resource_workschedules(
            "TEST_RES_001",
            {"recordType": "schedule", "scheduleLabel": "DAILY"},
        )

        assert isinstance(result, ResourceWorkScheduleResponse)

    @pytest.mark.asyncio
    async def test_set_resource_workschedules_uses_post(
        self, async_instance: AsyncOFSC
    ):
        """Test set_resource_workschedules uses POST."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [], "totalResults": 0}
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        await async_instance.core.set_resource_workschedules(
            "RES1", {"recordType": "schedule"}
        )

        assert async_instance.core._client.post.called
        url = async_instance.core._client.post.call_args.args[0]
        assert "workSchedules" in url


# ---------------------------------------------------------------------------
# bulk_update methods
# ---------------------------------------------------------------------------


class TestAsyncBulkUpdateResources:
    """Mocked tests for bulk_update_* methods."""

    @pytest.mark.asyncio
    async def test_bulk_update_workzones_returns_dict(self, mock_instance: AsyncOFSC):
        """Test bulk_update_resource_workzones returns dict."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.post = AsyncMock(return_value=mock_response)

        result = await mock_instance.core.bulk_update_resource_workzones(
            data={"items": []}
        )

        assert isinstance(result, dict)
        url = mock_instance.core._client.post.call_args.args[0]
        assert "bulkUpdateWorkZones" in url

    @pytest.mark.asyncio
    async def test_bulk_update_workskills_returns_dict(self, mock_instance: AsyncOFSC):
        """Test bulk_update_resource_workskills returns dict."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.post = AsyncMock(return_value=mock_response)

        result = await mock_instance.core.bulk_update_resource_workskills(
            data={"items": []}
        )

        assert isinstance(result, dict)
        url = mock_instance.core._client.post.call_args.args[0]
        assert "bulkUpdateWorkSkills" in url

    @pytest.mark.asyncio
    async def test_bulk_update_workschedules_returns_dict(
        self, async_instance: AsyncOFSC
    ):
        """Test bulk_update_resource_workschedules returns dict."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        result = await async_instance.core.bulk_update_resource_workschedules(
            data={"items": []}
        )

        assert isinstance(result, dict)
        url = async_instance.core._client.post.call_args.args[0]
        assert "bulkUpdateWorkSchedules" in url


# ---------------------------------------------------------------------------
# create_resource_location / delete_resource_location / update_resource_location
# ---------------------------------------------------------------------------


class TestAsyncResourceLocations:
    """Mocked tests for resource location methods."""

    @pytest.mark.asyncio
    async def test_create_resource_location_returns_location(
        self, async_instance: AsyncOFSC
    ):
        """Test create_resource_location returns Location model."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "label": "LOC001",
            "city": "Springfield",
            "country": "US",
            "locationId": 42,
        }
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        location = Location(label="LOC001", city="Springfield", country="US")
        result = await async_instance.core.create_resource_location(
            "RES1", location=location
        )

        assert isinstance(result, Location)
        assert result.city == "Springfield"
        assert result.locationId == 42

    @pytest.mark.asyncio
    async def test_create_resource_location_accepts_dict(
        self, async_instance: AsyncOFSC
    ):
        """Test create_resource_location accepts dict."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"label": "LOC002", "country": "US"}
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        result = await async_instance.core.create_resource_location(
            "RES1", location={"label": "LOC002", "country": "US"}
        )

        assert isinstance(result, Location)

    @pytest.mark.asyncio
    async def test_delete_resource_location_returns_none(
        self, async_instance: AsyncOFSC
    ):
        """Test delete_resource_location returns None on 204."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        async_instance.core._client.delete = AsyncMock(return_value=mock_response)

        result = await async_instance.core.delete_resource_location("RES1", 42)

        assert result is None
        url = async_instance.core._client.delete.call_args.args[0]
        assert "locations/42" in url

    @pytest.mark.asyncio
    async def test_update_resource_location_returns_location(
        self, async_instance: AsyncOFSC
    ):
        """Test update_resource_location returns Location model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "label": "LOC001",
            "city": "Shelbyville",
            "country": "US",
        }
        mock_response.raise_for_status = Mock()
        async_instance.core._client.patch = AsyncMock(return_value=mock_response)

        result = await async_instance.core.update_resource_location(
            "RES1", 42, {"city": "Shelbyville"}
        )

        assert isinstance(result, Location)
        assert result.city == "Shelbyville"
        url = async_instance.core._client.patch.call_args.args[0]
        assert "locations/42" in url


# ---------------------------------------------------------------------------
# set_assigned_locations
# ---------------------------------------------------------------------------


class TestAsyncSetAssignedLocations:
    """Mocked tests for set_assigned_locations."""

    @pytest.mark.asyncio
    async def test_set_assigned_locations_returns_response(
        self, async_instance: AsyncOFSC
    ):
        """Test set_assigned_locations returns AssignedLocationsResponse."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "mon": {"start": 1, "end": 2},
        }
        mock_response.raise_for_status = Mock()
        async_instance.core._client.put = AsyncMock(return_value=mock_response)

        result = await async_instance.core.set_assigned_locations(
            "RES1", {"mon": {"start": 1, "end": 2}}
        )

        assert isinstance(result, AssignedLocationsResponse)
        assert result.mon is not None

    @pytest.mark.asyncio
    async def test_set_assigned_locations_uses_put(self, mock_instance: AsyncOFSC):
        """Test set_assigned_locations uses PUT on assignedLocations endpoint."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.put = AsyncMock(return_value=mock_response)

        await mock_instance.core.set_assigned_locations("RES1", {})

        url = mock_instance.core._client.put.call_args.args[0]
        assert "assignedLocations" in url


# ---------------------------------------------------------------------------
# create_resource_inventory / install_resource_inventory
# ---------------------------------------------------------------------------


class TestAsyncResourceInventory:
    """Mocked tests for inventory write methods."""

    @pytest.mark.asyncio
    async def test_create_resource_inventory_returns_inventory(
        self, async_instance: AsyncOFSC
    ):
        """Test create_resource_inventory returns Inventory model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "inventoryId": 100,
            "inventoryType": "TOOL_A",
            "quantity": 1,
        }
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        result = await async_instance.core.create_resource_inventory(
            "RES1", {"inventoryType": "TOOL_A", "quantity": 1}
        )

        assert isinstance(result, Inventory)
        assert result.inventoryId == 100

    @pytest.mark.asyncio
    async def test_create_resource_inventory_uses_post(self, mock_instance: AsyncOFSC):
        """Test create_resource_inventory uses POST on inventories endpoint."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"inventoryId": 1, "inventoryType": "T"}
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.post = AsyncMock(return_value=mock_response)

        await mock_instance.core.create_resource_inventory(
            "RES1", {"inventoryType": "T"}
        )

        url = mock_instance.core._client.post.call_args.args[0]
        assert "inventories" in url and "RES1" in url

    @pytest.mark.asyncio
    async def test_install_resource_inventory_returns_inventory(
        self, async_instance: AsyncOFSC
    ):
        """Test install_resource_inventory returns Inventory model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "inventoryId": 100,
            "inventoryType": "TOOL_A",
        }
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        result = await async_instance.core.install_resource_inventory("RES1", 100)

        assert isinstance(result, Inventory)
        url = async_instance.core._client.post.call_args.args[0]
        assert "custom-actions/install" in url


# ---------------------------------------------------------------------------
# set_resource_workskills / delete_resource_workskill
# ---------------------------------------------------------------------------


class TestAsyncResourceWorkskills:
    """Mocked tests for workskill write methods."""

    @pytest.mark.asyncio
    async def test_set_resource_workskills_returns_list_response(
        self, async_instance: AsyncOFSC
    ):
        """Test set_resource_workskills returns ResourceWorkskillListResponse."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"workSkill": "ELEC", "ratio": 100}],
            "totalResults": 1,
        }
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        result = await async_instance.core.set_resource_workskills(
            "RES1", [{"workSkill": "ELEC", "ratio": 100}]
        )

        assert isinstance(result, ResourceWorkskillListResponse)
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_set_resource_workskills_body_format(self, mock_instance: AsyncOFSC):
        """Test set_resource_workskills sends items in correct format."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [], "totalResults": 0}
        mock_response.raise_for_status = Mock()
        mock_instance.core._client.post = AsyncMock(return_value=mock_response)

        await mock_instance.core.set_resource_workskills(
            "RES1", [{"workSkill": "PLUMB", "ratio": 50}]
        )

        call_kwargs = mock_instance.core._client.post.call_args
        assert "items" in call_kwargs.kwargs["json"]
        assert call_kwargs.kwargs["json"]["items"][0]["workSkill"] == "PLUMB"

    @pytest.mark.asyncio
    async def test_delete_resource_workskill_returns_none(
        self, async_instance: AsyncOFSC
    ):
        """Test delete_resource_workskill returns None on 204."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        async_instance.core._client.delete = AsyncMock(return_value=mock_response)

        result = await async_instance.core.delete_resource_workskill("RES1", "ELEC")

        assert result is None
        url = async_instance.core._client.delete.call_args.args[0]
        assert "workSkills/ELEC" in url


# ---------------------------------------------------------------------------
# set_resource_workzones / delete_resource_workzone
# ---------------------------------------------------------------------------


class TestAsyncResourceWorkzones:
    """Mocked tests for workzone write methods."""

    @pytest.mark.asyncio
    async def test_set_resource_workzones_returns_list_response(
        self, async_instance: AsyncOFSC
    ):
        """Test set_resource_workzones returns ResourceWorkzoneListResponse."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"workZone": "ZONE_A", "ratio": 100}],
            "totalResults": 1,
        }
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        result = await async_instance.core.set_resource_workzones(
            "RES1", [{"workZoneLabel": "ZONE_A", "ratio": 100}]
        )

        assert isinstance(result, ResourceWorkzoneListResponse)
        assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_delete_resource_workzone_returns_none(
        self, async_instance: AsyncOFSC
    ):
        """Test delete_resource_workzone returns None on 204."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        async_instance.core._client.delete = AsyncMock(return_value=mock_response)

        result = await async_instance.core.delete_resource_workzone("RES1", 99)

        assert result is None
        url = async_instance.core._client.delete.call_args.args[0]
        assert "workZones/99" in url


# ---------------------------------------------------------------------------
# delete_resource_workschedule
# ---------------------------------------------------------------------------


class TestAsyncDeleteResourceWorkschedule:
    """Mocked tests for delete_resource_workschedule."""

    @pytest.mark.asyncio
    async def test_delete_resource_workschedule_returns_none(
        self, async_instance: AsyncOFSC
    ):
        """Test delete_resource_workschedule returns None on 204."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        async_instance.core._client.delete = AsyncMock(return_value=mock_response)

        result = await async_instance.core.delete_resource_workschedule("RES1", 55)

        assert result is None
        url = async_instance.core._client.delete.call_args.args[0]
        assert "workSchedules/55" in url


# ---------------------------------------------------------------------------
# Exception handling tests
# ---------------------------------------------------------------------------


class TestAsyncResourceWriteExceptions:
    """Test exception handling for resource write/delete methods."""

    @pytest.mark.asyncio
    async def test_create_resource_404_raises_not_found(
        self, async_instance: AsyncOFSC
    ):
        """Test create_resource raises OFSCNotFoundError on 404."""
        http_error = _make_http_error(404, "Resource not found")
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Not found"}
        mock_response.text = "Not found"
        mock_response.raise_for_status = Mock(side_effect=http_error)
        async_instance.core._client.put = AsyncMock(return_value=mock_response)

        with pytest.raises(OFSCNotFoundError):
            await async_instance.core.create_resource("BAD_ID", _resource_payload())

    @pytest.mark.asyncio
    async def test_update_resource_404_raises_not_found(
        self, async_instance: AsyncOFSC
    ):
        """Test update_resource raises OFSCNotFoundError on 404."""
        http_error = _make_http_error(404, "Resource not found")
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Not found"}
        mock_response.text = "Not found"
        mock_response.raise_for_status = Mock(side_effect=http_error)
        async_instance.core._client.patch = AsyncMock(return_value=mock_response)

        with pytest.raises(OFSCNotFoundError):
            await async_instance.core.update_resource("BAD_ID", {"name": "X"})

    @pytest.mark.asyncio
    async def test_create_resource_400_raises_validation_error(
        self, async_instance: AsyncOFSC
    ):
        """Test create_resource raises pydantic.ValidationError for missing required fields."""
        # Empty dict is caught client-side by ResourceCreate before the API call
        with pytest.raises(pydantic.ValidationError):
            await async_instance.core.create_resource("RES1", {})

    @pytest.mark.asyncio
    async def test_create_resource_401_raises_authentication_error(
        self, async_instance: AsyncOFSC
    ):
        """Test create_resource raises OFSCAuthenticationError on 401."""
        http_error = _make_http_error(401, "Unauthorized")
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Unauthorized"}
        mock_response.text = "Unauthorized"
        mock_response.raise_for_status = Mock(side_effect=http_error)
        async_instance.core._client.put = AsyncMock(return_value=mock_response)

        with pytest.raises(OFSCAuthenticationError):
            await async_instance.core.create_resource("RES1", _resource_payload())

    @pytest.mark.asyncio
    async def test_delete_resource_users_network_error(self, mock_instance: AsyncOFSC):
        """Test delete_resource_users raises OFSCNetworkError on transport failure."""
        mock_instance.core._client.delete = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        with pytest.raises(OFSCNetworkError):
            await mock_instance.core.delete_resource_users("RES1")

    @pytest.mark.asyncio
    async def test_set_resource_workzones_network_error(
        self, async_instance: AsyncOFSC
    ):
        """Test set_resource_workzones raises OFSCNetworkError on transport failure."""
        async_instance.core._client.post = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        with pytest.raises(OFSCNetworkError):
            await async_instance.core.set_resource_workzones("RES1", [])


# ---------------------------------------------------------------------------
# Live tests (requires .env with API credentials)
# ---------------------------------------------------------------------------


class TestAsyncResourceWriteLive:
    """Live tests for resource write/delete operations.

    Requires API credentials in .env. Uses try/finally for cleanup.
    """

    _TEST_RESOURCE_ID = "CLAUDE_TEST_RES_001"

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_resources_then_create_update(self, async_instance: AsyncOFSC):
        """Test create_resource and update_resource against real API."""
        # Get a real resource to copy its structure
        resources = await async_instance.core.get_resources(limit=1)
        if not resources.items:
            pytest.skip("No resources available")

        sample = resources.items[0]
        if not sample.resourceId:
            pytest.skip("Sample resource has no resourceId")

        # Create a test resource with minimal required fields
        create_data = ResourceCreate(
            parentResourceId=sample.resourceId,
            resourceType=sample.resourceType,
            name="Claude Test Resource",
            language=sample.language,
            timeZone=sample.timeZone,
            status="inactive",
        )

        try:
            created = await async_instance.core.create_resource(
                self._TEST_RESOURCE_ID, create_data
            )
            assert isinstance(created, Resource)
            assert created.name == "Claude Test Resource"

            # Update it
            updated = await async_instance.core.update_resource(
                self._TEST_RESOURCE_ID, {"name": "Claude Test Resource Updated"}
            )
            assert isinstance(updated, Resource)
            assert updated.name == "Claude Test Resource Updated"

        finally:
            # Mark as inactive — OFSC typically doesn't allow deleting resources
            try:
                await async_instance.core.update_resource(
                    self._TEST_RESOURCE_ID, {"status": "inactive"}
                )
            except Exception:
                pass

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_set_delete_resource_users_live(self, async_instance: AsyncOFSC):
        """Test set_resource_users and delete_resource_users against real API."""
        resources = await async_instance.core.get_resources(limit=1)
        if not resources.items:
            pytest.skip("No resources available")

        resource_id = resources.items[0].resourceId
        if not resource_id:
            pytest.skip("Resource has no resourceId")

        # Get current users so we can restore
        current = await async_instance.core.get_resource_users(resource_id)
        original_logins = [item.login for item in current.items]

        try:
            # Delete users
            await async_instance.core.delete_resource_users(resource_id)
            after_delete = await async_instance.core.get_resource_users(resource_id)
            assert len(after_delete.items) == 0

        except OFSCConflictError:
            pytest.skip("Conflict error — resource may be in use, skipping")

        finally:
            # Restore original users
            if original_logins:
                await async_instance.core.set_resource_users(
                    resource_id=resource_id, users=original_logins
                )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_create_delete_resource_location_live(
        self, async_instance: AsyncOFSC
    ):
        """Test create_resource_location and delete_resource_location against real API."""
        resources = await async_instance.core.get_resources(limit=1)
        if not resources.items:
            pytest.skip("No resources available")

        resource_id = resources.items[0].resourceId
        if not resource_id:
            pytest.skip("Resource has no resourceId")

        new_location = Location(
            label=f"CLAUDE_TEST_LOC_{resource_id}",
            city="Test City",
            country="US",
        )

        created_location = await async_instance.core.create_resource_location(
            resource_id, location=new_location
        )
        assert isinstance(created_location, Location)
        assert created_location.locationId is not None

        try:
            # Update it
            updated = await async_instance.core.update_resource_location(
                resource_id, created_location.locationId, {"city": "Updated City"}
            )
            assert isinstance(updated, Location)

        finally:
            # Delete it
            if created_location.locationId:
                await async_instance.core.delete_resource_location(
                    resource_id, created_location.locationId
                )


class TestAsyncResourceFileProperty:
    """Mocked tests for resource file property methods."""

    @pytest.mark.asyncio
    async def test_get_resource_file_property_returns_bytes(
        self, async_instance: AsyncOFSC
    ):
        """Test get_resource_file_property returns bytes."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"fake_binary_data"
        mock_response.raise_for_status = Mock()
        async_instance.core._client.get = AsyncMock(return_value=mock_response)

        result = await async_instance.core.get_resource_file_property("RES001", "csign")

        assert isinstance(result, bytes)
        assert result == b"fake_binary_data"

        call_kwargs = async_instance.core._client.get.call_args
        assert call_kwargs.kwargs["headers"]["Accept"] == "application/octet-stream"

    @pytest.mark.asyncio
    async def test_set_resource_file_property_returns_none(
        self, async_instance: AsyncOFSC
    ):
        """Test set_resource_file_property returns None on success (204)."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        async_instance.core._client.put = AsyncMock(return_value=mock_response)

        result = await async_instance.core.set_resource_file_property(
            "RES001",
            "csign",
            b"image_data",
            "signature.png",
            "image/png",
        )

        assert result is None

        call_kwargs = async_instance.core._client.put.call_args
        headers = call_kwargs.kwargs["headers"]
        assert headers["Content-Type"] == "image/png"
        assert 'filename="signature.png"' in headers["Content-Disposition"]

    @pytest.mark.asyncio
    async def test_delete_resource_file_property_returns_none(
        self, async_instance: AsyncOFSC
    ):
        """Test delete_resource_file_property returns None on success (204)."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        async_instance.core._client.delete = AsyncMock(return_value=mock_response)

        result = await async_instance.core.delete_resource_file_property(
            "RES001", "csign"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_set_resource_file_property_not_found(
        self, async_instance: AsyncOFSC
    ):
        """Test set_resource_file_property raises OFSCNotFoundError on 404."""
        async_instance.core._client.put = AsyncMock(
            side_effect=_make_http_error(404, "Resource not found")
        )

        with pytest.raises(OFSCNotFoundError):
            await async_instance.core.set_resource_file_property(
                "NONEXISTENT", "csign", b"data", "file.bin"
            )

    @pytest.mark.asyncio
    async def test_delete_resource_file_property_not_found(
        self, async_instance: AsyncOFSC
    ):
        """Test delete_resource_file_property raises OFSCNotFoundError on 404."""
        async_instance.core._client.delete = AsyncMock(
            side_effect=_make_http_error(404, "Resource not found")
        )

        with pytest.raises(OFSCNotFoundError):
            await async_instance.core.delete_resource_file_property(
                "NONEXISTENT", "csign"
            )


class TestAsyncResourceFilePropertyLive:
    """Live roundtrip tests for resource file property methods.

    Requires API credentials in .env and a file-type property on resources.
    """

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_set_get_delete_roundtrip(
        self, async_instance: AsyncOFSC, resource_file_property_label: str
    ):
        """Test set → get → verify → delete roundtrip for resource file property."""
        resources = await async_instance.core.get_resources(limit=1)
        if not resources.items:
            pytest.skip("No resources available")

        resource_id = resources.items[0].resourceId
        if not resource_id:
            pytest.skip("Resource has no resourceId")

        content = b"CLAUDE_TEST_BINARY_CONTENT"
        filename = "test_signature.bin"

        await async_instance.core.set_resource_file_property(
            resource_id,
            resource_file_property_label,
            content,
            filename,
        )

        try:
            fetched = await async_instance.core.get_resource_file_property(
                resource_id, resource_file_property_label
            )
            assert isinstance(fetched, bytes)
            assert fetched == content
        finally:
            try:
                await async_instance.core.delete_resource_file_property(
                    resource_id, resource_file_property_label
                )
            except Exception:
                pass
