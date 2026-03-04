"""Async tests for standalone inventory operations."""

from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import (
    OFSCAuthenticationError,
    OFSCNetworkError,
    OFSCNotFoundError,
)
from ofsc.models import (
    Inventory,
    InventoryCreate,
    InventoryCustomAction,
)

import httpx


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class TestInventoryCreateModel:
    """Test InventoryCreate model validation."""

    def test_inventory_create_requires_inventory_type(self):
        """Test that InventoryCreate requires inventoryType."""
        with pytest.raises(Exception):
            InventoryCreate.model_validate({"resourceId": "RES1"})

    def test_inventory_create_requires_context(self):
        """Test that InventoryCreate requires at least one context field."""
        with pytest.raises(Exception):
            InventoryCreate.model_validate({"inventoryType": "PART_A"})

    def test_inventory_create_valid_with_resource_id(self):
        """Test InventoryCreate with inventoryType and resourceId."""
        inv = InventoryCreate.model_validate(
            {"inventoryType": "PART_A", "resourceId": "RES1"}
        )
        assert inv.inventoryType == "PART_A"
        assert inv.resourceId == "RES1"

    def test_inventory_create_valid_with_activity_id(self):
        """Test InventoryCreate with inventoryType and activityId."""
        inv = InventoryCreate.model_validate(
            {"inventoryType": "PART_A", "activityId": 12345}
        )
        assert inv.inventoryType == "PART_A"
        assert inv.activityId == 12345

    def test_inventory_create_valid_with_resource_internal_id(self):
        """Test InventoryCreate with inventoryType and resourceInternalId."""
        inv = InventoryCreate.model_validate(
            {"inventoryType": "PART_A", "resourceInternalId": 99}
        )
        assert inv.inventoryType == "PART_A"
        assert inv.resourceInternalId == 99

    def test_inventory_create_with_optional_fields(self):
        """Test InventoryCreate with all optional fields."""
        inv = InventoryCreate.model_validate(
            {
                "inventoryType": "PART_B",
                "resourceId": "RES1",
                "activityId": 12345,
                "status": "resource",
                "serialNumber": "SN-001",
                "quantity": 2.0,
            }
        )
        assert inv.inventoryType == "PART_B"
        assert inv.resourceId == "RES1"
        assert inv.activityId == 12345
        assert inv.quantity == 2.0
        assert inv.serialNumber == "SN-001"

    def test_inventory_create_model_dump_excludes_none(self):
        """Test that model_dump with exclude_none works correctly."""
        inv = InventoryCreate.model_validate(
            {"inventoryType": "PART_C", "resourceId": "RES1"}
        )
        dumped = inv.model_dump(exclude_none=True)
        assert "inventoryType" in dumped
        assert "resourceId" in dumped
        assert "activityId" not in dumped


class TestInventoryCustomActionModel:
    """Test InventoryCustomAction model validation."""

    def test_inventory_custom_action_empty(self):
        """Test InventoryCustomAction with no fields (all optional)."""
        action = InventoryCustomAction.model_validate({})
        assert action.activityId is None
        assert action.quantity is None

    def test_inventory_custom_action_with_fields(self):
        """Test InventoryCustomAction with optional fields."""
        action = InventoryCustomAction.model_validate(
            {"activityId": 99, "quantity": 1.5}
        )
        assert action.activityId == 99
        assert action.quantity == 1.5

    def test_inventory_custom_action_model_dump_excludes_none(self):
        """Test model_dump with exclude_none."""
        action = InventoryCustomAction.model_validate({"activityId": 42})
        dumped = action.model_dump(exclude_none=True)
        assert "activityId" in dumped
        assert "quantity" not in dumped


# ---------------------------------------------------------------------------
# Mocked CRUD tests
# ---------------------------------------------------------------------------


class TestAsyncCreateInventory:
    """Mocked tests for create_inventory."""

    @pytest.mark.asyncio
    async def test_create_inventory_with_model(self, async_instance: AsyncOFSC):
        """Test create_inventory with InventoryCreate model."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "inventoryId": 101,
            "inventoryType": "PART_A",
            "status": "resource",
            "resourceId": "RES1",
        }
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        data = InventoryCreate.model_validate(
            {"inventoryType": "PART_A", "resourceId": "RES1"}
        )
        result = await async_instance.core.create_inventory(data)

        assert isinstance(result, Inventory)
        assert result.inventoryId == 101
        assert result.inventoryType == "PART_A"

    @pytest.mark.asyncio
    async def test_create_inventory_with_dict(self, async_instance: AsyncOFSC):
        """Test create_inventory with dict input (auto-validates)."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "inventoryId": 102,
            "inventoryType": "PART_B",
        }
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        result = await async_instance.core.create_inventory(
            {"inventoryType": "PART_B", "resourceId": "RES2"}
        )

        assert isinstance(result, Inventory)
        assert result.inventoryId == 102

    @pytest.mark.asyncio
    async def test_create_inventory_sends_correct_body(self, async_instance: AsyncOFSC):
        """Test that create_inventory sends the correct JSON body."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "inventoryId": 103,
            "inventoryType": "PART_C",
        }
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        await async_instance.core.create_inventory(
            {"inventoryType": "PART_C", "resourceId": "RES3", "quantity": 3.0}
        )

        call_kwargs = async_instance.core._client.post.call_args
        assert call_kwargs.kwargs["json"]["inventoryType"] == "PART_C"
        assert call_kwargs.kwargs["json"]["quantity"] == 3.0


class TestAsyncGetInventory:
    """Mocked tests for get_inventory."""

    @pytest.mark.asyncio
    async def test_get_inventory_returns_model(self, async_instance: AsyncOFSC):
        """Test that get_inventory returns Inventory model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "inventoryId": 55,
            "inventoryType": "PART_X",
            "status": "installed",
            "quantity": 1.0,
        }
        mock_response.raise_for_status = Mock()
        async_instance.core._client.get = AsyncMock(return_value=mock_response)

        result = await async_instance.core.get_inventory(55)

        assert isinstance(result, Inventory)
        assert result.inventoryId == 55
        assert result.inventoryType == "PART_X"
        assert result.status == "installed"

    @pytest.mark.asyncio
    async def test_get_inventory_url(self, async_instance: AsyncOFSC):
        """Test that get_inventory uses correct URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"inventoryId": 77}
        mock_response.raise_for_status = Mock()
        async_instance.core._client.get = AsyncMock(return_value=mock_response)

        await async_instance.core.get_inventory(77)

        call_args = async_instance.core._client.get.call_args
        assert "/rest/ofscCore/v1/inventories/77" in call_args.args[0]


class TestAsyncUpdateInventory:
    """Mocked tests for update_inventory."""

    @pytest.mark.asyncio
    async def test_update_inventory_returns_model(self, async_instance: AsyncOFSC):
        """Test that update_inventory returns updated Inventory model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "inventoryId": 88,
            "inventoryType": "PART_Y",
            "status": "resource",
            "quantity": 5.0,
        }
        mock_response.raise_for_status = Mock()
        async_instance.core._client.patch = AsyncMock(return_value=mock_response)

        result = await async_instance.core.update_inventory(88, {"quantity": 5.0})

        assert isinstance(result, Inventory)
        assert result.inventoryId == 88
        assert result.quantity == 5.0

    @pytest.mark.asyncio
    async def test_update_inventory_sends_patch(self, async_instance: AsyncOFSC):
        """Test that update_inventory sends PATCH request with correct body."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"inventoryId": 99}
        mock_response.raise_for_status = Mock()
        async_instance.core._client.patch = AsyncMock(return_value=mock_response)

        await async_instance.core.update_inventory(99, {"serialNumber": "SN-999"})

        call_kwargs = async_instance.core._client.patch.call_args
        assert call_kwargs.kwargs["json"] == {"serialNumber": "SN-999"}


class TestAsyncDeleteInventory:
    """Mocked tests for delete_inventory."""

    @pytest.mark.asyncio
    async def test_delete_inventory_returns_none(self, async_instance: AsyncOFSC):
        """Test that delete_inventory returns None on success."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        async_instance.core._client.delete = AsyncMock(return_value=mock_response)

        result = await async_instance.core.delete_inventory(42)

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_inventory_url(self, async_instance: AsyncOFSC):
        """Test that delete_inventory uses correct URL."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        async_instance.core._client.delete = AsyncMock(return_value=mock_response)

        await async_instance.core.delete_inventory(42)

        call_args = async_instance.core._client.delete.call_args
        assert "/rest/ofscCore/v1/inventories/42" in call_args.args[0]


# ---------------------------------------------------------------------------
# Mocked file property tests
# ---------------------------------------------------------------------------


class TestAsyncInventoryProperties:
    """Mocked tests for inventory file properties."""

    @pytest.mark.asyncio
    async def test_get_inventory_property_returns_bytes(
        self, async_instance: AsyncOFSC
    ):
        """Test that get_inventory_property returns bytes."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"binary_data_here"
        mock_response.raise_for_status = Mock()
        async_instance.core._client.get = AsyncMock(return_value=mock_response)

        result = await async_instance.core.get_inventory_property(10, "photo")

        assert isinstance(result, bytes)
        assert result == b"binary_data_here"

    @pytest.mark.asyncio
    async def test_get_inventory_property_sets_accept_header(
        self, async_instance: AsyncOFSC
    ):
        """Test that get_inventory_property sets Accept header."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"data"
        mock_response.raise_for_status = Mock()
        async_instance.core._client.get = AsyncMock(return_value=mock_response)

        await async_instance.core.get_inventory_property(10, "photo")

        call_kwargs = async_instance.core._client.get.call_args
        assert call_kwargs.kwargs["headers"]["Accept"] == "application/octet-stream"

    @pytest.mark.asyncio
    async def test_set_inventory_property_returns_none(self, async_instance: AsyncOFSC):
        """Test that set_inventory_property returns None on success."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        async_instance.core._client.put = AsyncMock(return_value=mock_response)

        result = await async_instance.core.set_inventory_property(
            10, "photo", b"image_bytes", "photo.jpg"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_set_inventory_property_content_disposition(
        self, async_instance: AsyncOFSC
    ):
        """Test that set_inventory_property sets Content-Disposition header."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        async_instance.core._client.put = AsyncMock(return_value=mock_response)

        await async_instance.core.set_inventory_property(
            10, "photo", b"data", "my_photo.png", "image/png"
        )

        call_kwargs = async_instance.core._client.put.call_args
        assert "Content-Disposition" in call_kwargs.kwargs["headers"]
        assert "my_photo.png" in call_kwargs.kwargs["headers"]["Content-Disposition"]
        assert call_kwargs.kwargs["headers"]["Content-Type"] == "image/png"

    @pytest.mark.asyncio
    async def test_delete_inventory_property_returns_none(
        self, async_instance: AsyncOFSC
    ):
        """Test that delete_inventory_property returns None on success."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        async_instance.core._client.delete = AsyncMock(return_value=mock_response)

        result = await async_instance.core.delete_inventory_property(10, "photo")

        assert result is None


# ---------------------------------------------------------------------------
# Mocked custom action tests
# ---------------------------------------------------------------------------


class TestAsyncInventoryCustomActions:
    """Mocked tests for inventory custom actions."""

    @pytest.mark.asyncio
    async def test_inventory_install_returns_model(self, async_instance: AsyncOFSC):
        """Test inventory_install returns Inventory model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "inventoryId": 20,
            "inventoryType": "PART_A",
            "status": "installed",
        }
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        result = await async_instance.core.inventory_install(20)

        assert isinstance(result, Inventory)
        assert result.inventoryId == 20
        assert result.status == "installed"

    @pytest.mark.asyncio
    async def test_inventory_install_url(self, async_instance: AsyncOFSC):
        """Test inventory_install uses correct URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"inventoryId": 20}
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        await async_instance.core.inventory_install(20)

        call_args = async_instance.core._client.post.call_args
        assert "custom-actions/install" in call_args.args[0]

    @pytest.mark.asyncio
    async def test_inventory_install_with_data(self, async_instance: AsyncOFSC):
        """Test inventory_install with InventoryCustomAction data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"inventoryId": 21, "activityId": 500}
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        action = InventoryCustomAction.model_validate({"activityId": 500})
        result = await async_instance.core.inventory_install(21, action)

        assert isinstance(result, Inventory)
        call_kwargs = async_instance.core._client.post.call_args
        assert call_kwargs.kwargs["json"]["activityId"] == 500

    @pytest.mark.asyncio
    async def test_inventory_deinstall_returns_model(self, async_instance: AsyncOFSC):
        """Test inventory_deinstall returns Inventory model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "inventoryId": 30,
            "status": "deinstalled",
        }
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        result = await async_instance.core.inventory_deinstall(30)

        assert isinstance(result, Inventory)
        assert result.inventoryId == 30

    @pytest.mark.asyncio
    async def test_inventory_deinstall_url(self, async_instance: AsyncOFSC):
        """Test inventory_deinstall uses correct URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"inventoryId": 30}
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        await async_instance.core.inventory_deinstall(30)

        call_args = async_instance.core._client.post.call_args
        assert "custom-actions/deinstall" in call_args.args[0]

    @pytest.mark.asyncio
    async def test_inventory_undo_install_url(self, async_instance: AsyncOFSC):
        """Test inventory_undo_install uses correct URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"inventoryId": 40}
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        await async_instance.core.inventory_undo_install(40)

        call_args = async_instance.core._client.post.call_args
        assert "custom-actions/undoInstall" in call_args.args[0]

    @pytest.mark.asyncio
    async def test_inventory_undo_deinstall_url(self, async_instance: AsyncOFSC):
        """Test inventory_undo_deinstall uses correct URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"inventoryId": 50}
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        await async_instance.core.inventory_undo_deinstall(50)

        call_args = async_instance.core._client.post.call_args
        assert "custom-actions/undoDeinstall" in call_args.args[0]

    @pytest.mark.asyncio
    async def test_custom_action_with_dict_data(self, async_instance: AsyncOFSC):
        """Test custom action accepts dict as data (auto-validates)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"inventoryId": 60}
        mock_response.raise_for_status = Mock()
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        result = await async_instance.core.inventory_install(
            60, {"activityId": 999, "quantity": 1.0}
        )

        assert isinstance(result, Inventory)
        call_kwargs = async_instance.core._client.post.call_args
        assert call_kwargs.kwargs["json"]["activityId"] == 999


# ---------------------------------------------------------------------------
# Exception tests
# ---------------------------------------------------------------------------


class TestAsyncInventoryExceptions:
    """Exception handling tests for inventory operations."""

    @pytest.mark.asyncio
    async def test_get_inventory_not_found(self, async_instance: AsyncOFSC):
        """Test that get_inventory raises OFSCNotFoundError on 404."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            "type": "https://ofsc/error/not-found",
            "title": "Not Found",
            "detail": "Inventory not found",
        }
        mock_response.raise_for_status = Mock(
            side_effect=httpx.HTTPStatusError(
                "404", request=Mock(), response=mock_response
            )
        )
        async_instance.core._client.get = AsyncMock(return_value=mock_response)

        with pytest.raises(OFSCNotFoundError):
            await async_instance.core.get_inventory(99999)

    @pytest.mark.asyncio
    async def test_get_inventory_authentication_error(self, async_instance: AsyncOFSC):
        """Test that get_inventory raises OFSCAuthenticationError on 401."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"title": "Unauthorized"}
        mock_response.raise_for_status = Mock(
            side_effect=httpx.HTTPStatusError(
                "401", request=Mock(), response=mock_response
            )
        )
        async_instance.core._client.get = AsyncMock(return_value=mock_response)

        with pytest.raises(OFSCAuthenticationError):
            await async_instance.core.get_inventory(1)

    @pytest.mark.asyncio
    async def test_get_inventory_network_error(self, async_instance: AsyncOFSC):
        """Test that network errors raise OFSCNetworkError."""
        async_instance.core._client.get = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        with pytest.raises(OFSCNetworkError):
            await async_instance.core.get_inventory(1)

    @pytest.mark.asyncio
    async def test_create_inventory_network_error(self, async_instance: AsyncOFSC):
        """Test that network errors on create raise OFSCNetworkError."""
        async_instance.core._client.post = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        with pytest.raises(OFSCNetworkError):
            await async_instance.core.create_inventory(
                {"inventoryType": "PART_A", "resourceId": "RES1"}
            )

    @pytest.mark.asyncio
    async def test_delete_inventory_not_found(self, async_instance: AsyncOFSC):
        """Test that delete_inventory raises OFSCNotFoundError on 404."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"title": "Not Found"}
        mock_response.raise_for_status = Mock(
            side_effect=httpx.HTTPStatusError(
                "404", request=Mock(), response=mock_response
            )
        )
        async_instance.core._client.delete = AsyncMock(return_value=mock_response)

        with pytest.raises(OFSCNotFoundError):
            await async_instance.core.delete_inventory(99999)

    @pytest.mark.asyncio
    async def test_inventory_install_not_found(self, async_instance: AsyncOFSC):
        """Test that inventory_install raises OFSCNotFoundError on 404."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"title": "Not Found"}
        mock_response.raise_for_status = Mock(
            side_effect=httpx.HTTPStatusError(
                "404", request=Mock(), response=mock_response
            )
        )
        async_instance.core._client.post = AsyncMock(return_value=mock_response)

        with pytest.raises(OFSCNotFoundError):
            await async_instance.core.inventory_install(99999)


# ---------------------------------------------------------------------------
# Live tests (requires API credentials)
# ---------------------------------------------------------------------------


class TestAsyncInventoriesLive:
    """Live tests against actual API — require API credentials."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_serialized_inventory_crud_lifecycle(
        self, async_instance: AsyncOFSC, serialized_inventory_type: str
    ):
        """Test full CRUD lifecycle for a serialized inventory type."""
        resources = await async_instance.core.get_resources(limit=1)
        if not resources.items:
            pytest.skip("No resources available")

        sample = resources.items[0]
        if not sample.resourceId:
            pytest.skip("Sample resource has no resourceId")

        created_id = None
        try:
            inv = await async_instance.core.create_inventory(
                {
                    "inventoryType": serialized_inventory_type,
                    "resourceId": sample.resourceId,
                }
            )
            assert isinstance(inv, Inventory)
            assert inv.inventoryId is not None
            created_id = inv.inventoryId

            fetched = await async_instance.core.get_inventory(created_id)
            assert isinstance(fetched, Inventory)
            assert fetched.inventoryId == created_id

            updated = await async_instance.core.update_inventory(
                created_id, {"serialNumber": "SN-TEST-001"}
            )
            assert isinstance(updated, Inventory)

        finally:
            if created_id is not None:
                await async_instance.core.delete_inventory(created_id)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_non_serialized_inventory_crud_lifecycle(
        self, async_instance: AsyncOFSC, non_serialized_inventory_type: str
    ):
        """Test full CRUD lifecycle for a non-serialized inventory type."""
        resources = await async_instance.core.get_resources(limit=1)
        if not resources.items:
            pytest.skip("No resources available")

        sample = resources.items[0]
        if not sample.resourceId:
            pytest.skip("Sample resource has no resourceId")

        created_id = None
        try:
            inv = await async_instance.core.create_inventory(
                {
                    "inventoryType": non_serialized_inventory_type,
                    "resourceId": sample.resourceId,
                }
            )
            assert isinstance(inv, Inventory)
            assert inv.inventoryId is not None
            created_id = inv.inventoryId

            fetched = await async_instance.core.get_inventory(created_id)
            assert isinstance(fetched, Inventory)
            assert fetched.inventoryId == created_id

            updated = await async_instance.core.update_inventory(
                created_id, {"quantity": 5.0}
            )
            assert isinstance(updated, Inventory)

        finally:
            if created_id is not None:
                await async_instance.core.delete_inventory(created_id)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_inventory_not_found_live(self, async_instance: AsyncOFSC):
        """Test get_inventory with non-existent ID raises OFSCNotFoundError."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.core.get_inventory(999999999)
