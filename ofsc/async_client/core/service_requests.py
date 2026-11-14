"""Async service request methods mixin for OFSCore API."""

from typing import Union
from urllib.parse import quote_plus, urljoin

import httpx

from ...exceptions import OFSCNetworkError
from ...models.service_requests import ServiceRequest, ServiceRequestCreate
from .._protocols import _CoreBaseProtocol


class AsyncOFSCoreServiceRequestsMixin:
    """Mixin providing async service request methods for AsyncOFSCore.

    Requires _client, baseUrl, headers, and _handle_http_error from base class.
    """

    # region Service Requests

    async def create_service_request(self: _CoreBaseProtocol, data: Union[ServiceRequestCreate, dict]) -> ServiceRequest:
        """Create a service request (CO078P).

        Exactly one of activityId, resourceId or inventoryId must be provided.

        Args:
            data: ServiceRequestCreate model or dict (custom properties allowed)

        Returns:
            ServiceRequest: The created service request

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If the referenced entity is not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        if isinstance(data, dict):
            data = ServiceRequestCreate.model_validate(data)
        body = data.model_dump(exclude_none=True, mode="json")
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/serviceRequests")

        try:
            response = await self._client.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            return ServiceRequest.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to create service request")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_service_request(self: _CoreBaseProtocol, request_id: int) -> ServiceRequest:
        """Get a service request (CO077G).

        Args:
            request_id: Service request identifier

        Returns:
            ServiceRequest: The service request

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If the service request is not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/serviceRequests/{request_id}")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            return ServiceRequest.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get service request {request_id}")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_service_request_property(
        self: _CoreBaseProtocol,
        request_id: int,
        property_label: str,
        media_type: str = "application/octet-stream",
    ) -> bytes:
        """Get a binary file property of a service request (CO079G).

        Args:
            request_id: Service request identifier
            property_label: Property label
            media_type: Expected MIME type (default: application/octet-stream)

        Returns:
            bytes: Binary content of the property

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If request or property not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_label = quote_plus(property_label)
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/serviceRequests/{request_id}/{encoded_label}")
        headers = {**self.headers, "Accept": media_type}

        try:
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()
            return response.content
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e,
                f"Failed to get property '{property_label}' for service request {request_id}",
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion
