"""Async inventory methods mixin for OFSCore API."""

from typing import Optional, Protocol
from urllib.parse import urljoin

import httpx

from ...exceptions import (
    OFSCNetworkError,
)
from ...models.inventories import (
    Inventory,
    InventoryCreate,
    InventoryCustomAction,
)


class _CoreBaseProtocol(Protocol):
    """Type stub declaring what AsyncOFSCoreInventoriesMixin expects from its base class."""

    _client: httpx.AsyncClient
    baseUrl: str
    headers: dict

    def _handle_http_error(self, e: httpx.HTTPStatusError, context: str = "") -> None: ...

    async def _inventory_custom_action(
        self,
        inventory_id: int,
        action: str,
        data: Optional["InventoryCustomAction | dict"] = None,
    ) -> "Inventory": ...


class AsyncOFSCoreInventoriesMixin:
    """Mixin providing async standalone inventory methods for AsyncOFSCore.

    Requires _client, baseUrl, headers, and _handle_http_error from base class.
    These are standalone inventory endpoints under /rest/ofscCore/v1/inventories/,
    distinct from resource-scoped and activity-scoped inventory methods.
    """

    # region Inventories

    async def create_inventory(self: _CoreBaseProtocol, data: "InventoryCreate | dict") -> Inventory:
        """Create a new inventory item.

        Args:
            data: Inventory data as InventoryCreate model or dict

        Returns:
            Inventory: Created inventory item

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCValidationError: If data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        if isinstance(data, dict):
            data = InventoryCreate.model_validate(data)
        body = data.model_dump(exclude_none=True)

        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/inventories")

        try:
            response = await self._client.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            return Inventory.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to create inventory")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_inventory(self: _CoreBaseProtocol, inventory_id: int) -> Inventory:
        """Get a single inventory item by ID.

        Args:
            inventory_id: Inventory ID

        Returns:
            Inventory: Inventory item details

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If inventory not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/inventories/{inventory_id}")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            return Inventory.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get inventory {inventory_id}")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def update_inventory(self: _CoreBaseProtocol, inventory_id: int, data: dict) -> Inventory:
        """Update an inventory item (PATCH — partial update).

        Args:
            inventory_id: Inventory ID
            data: Partial inventory data to update

        Returns:
            Inventory: Updated inventory item

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If inventory not found (404)
            OFSCValidationError: If data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/inventories/{inventory_id}")

        try:
            response = await self._client.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
            return Inventory.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to update inventory {inventory_id}")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_inventory(self: _CoreBaseProtocol, inventory_id: int) -> None:
        """Delete an inventory item.

        Args:
            inventory_id: Inventory ID

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If inventory not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/inventories/{inventory_id}")

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to delete inventory {inventory_id}")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # region File Properties

    async def get_inventory_property(self: _CoreBaseProtocol, inventory_id: int, label: str) -> bytes:
        """Get a binary file property for an inventory item.

        Args:
            inventory_id: Inventory ID
            label: Property label

        Returns:
            bytes: Binary content of the property

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If inventory or property not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/inventories/{inventory_id}/{label}")
        headers = {**self.headers, "Accept": "application/octet-stream"}

        try:
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()
            return response.content
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get property '{label}' for inventory {inventory_id}")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def set_inventory_property(
        self: _CoreBaseProtocol,
        inventory_id: int,
        label: str,
        content: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
    ) -> None:
        """Upload a binary file property for an inventory item.

        Args:
            inventory_id: Inventory ID
            label: Property label
            content: Binary content to upload
            filename: Filename for the Content-Disposition header
            content_type: MIME type of the content (default: application/octet-stream)

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If inventory not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/inventories/{inventory_id}/{label}")
        base_headers = {k: v for k, v in self.headers.items() if k != "Content-Type"}
        headers = {
            **base_headers,
            "Content-Type": content_type,
            "Content-Disposition": f'attachment; filename="{filename}"',
        }

        try:
            response = await self._client.put(url, headers=headers, content=content)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to set property '{label}' for inventory {inventory_id}")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_inventory_property(self: _CoreBaseProtocol, inventory_id: int, label: str) -> None:
        """Delete a binary file property for an inventory item.

        Args:
            inventory_id: Inventory ID
            label: Property label to delete

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If inventory or property not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/inventories/{inventory_id}/{label}")

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to delete property '{label}' for inventory {inventory_id}")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Custom Actions

    async def _inventory_custom_action(
        self: _CoreBaseProtocol,
        inventory_id: int,
        action: str,
        data: Optional["InventoryCustomAction | dict"] = None,
    ) -> Inventory:
        """Internal helper for inventory custom actions."""
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/inventories/{inventory_id}/custom-actions/{action}",
        )
        body = None
        if data is not None:
            if isinstance(data, dict):
                data = InventoryCustomAction.model_validate(data)
            body = data.model_dump(exclude_none=True)

        try:
            response = await self._client.post(url, headers=self.headers, json=body or {})
            response.raise_for_status()
            return Inventory.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to perform '{action}' on inventory {inventory_id}",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def inventory_install(
        self: _CoreBaseProtocol,
        inventory_id: int,
        data: Optional["InventoryCustomAction | dict"] = None,
    ) -> Inventory:
        """Install an inventory item (POST custom-action).

        Args:
            inventory_id: Inventory ID
            data: Optional action parameters (activityId, quantity)

        Returns:
            Inventory: Updated inventory item

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If inventory not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        return await self._inventory_custom_action(inventory_id, "install", data)

    async def inventory_deinstall(
        self: _CoreBaseProtocol,
        inventory_id: int,
        data: Optional["InventoryCustomAction | dict"] = None,
    ) -> Inventory:
        """Deinstall an inventory item (POST custom-action).

        Args:
            inventory_id: Inventory ID
            data: Optional action parameters (activityId, quantity)

        Returns:
            Inventory: Updated inventory item

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If inventory not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        return await self._inventory_custom_action(inventory_id, "deinstall", data)

    async def inventory_undo_install(
        self: _CoreBaseProtocol,
        inventory_id: int,
        data: Optional["InventoryCustomAction | dict"] = None,
    ) -> Inventory:
        """Undo install of an inventory item (POST custom-action).

        Args:
            inventory_id: Inventory ID
            data: Optional action parameters (activityId, quantity)

        Returns:
            Inventory: Updated inventory item

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If inventory not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        return await self._inventory_custom_action(inventory_id, "undoInstall", data)

    async def inventory_undo_deinstall(
        self: _CoreBaseProtocol,
        inventory_id: int,
        data: Optional["InventoryCustomAction | dict"] = None,
    ) -> Inventory:
        """Undo deinstall of an inventory item (POST custom-action).

        Args:
            inventory_id: Inventory ID
            data: Optional action parameters (activityId, quantity)

        Returns:
            Inventory: Updated inventory item

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If inventory not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        return await self._inventory_custom_action(inventory_id, "undoDeinstall", data)

    # endregion

    # endregion
