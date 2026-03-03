"""Async user methods mixin for OFSCore API."""

from urllib.parse import quote_plus, urljoin

import httpx

from ...exceptions import (
    OFSCNetworkError,
)
from ...models import (
    CollaborationGroupsResponse,
    User,
    UserCreate,
    UserListResponse,
)


class AsyncOFSCoreUsersMixin:
    """Mixin providing async user-related methods for AsyncOFSCore.

    Requires _client, baseUrl, headers, and _handle_http_error from base class.
    """

    # region Users

    async def get_users(self, offset: int = 0, limit: int = 100) -> UserListResponse:
        """Get a paginated list of users.

        Args:
            offset: Starting record number (default 0)
            limit: Maximum number to return (default 100)

        Returns:
            UserListResponse: List with pagination info

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        url = urljoin(self.baseUrl, "/rest/ofscCore/v1/users")
        params = {"offset": offset, "limit": limit}

        try:
            response = await self._client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return UserListResponse.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, "Failed to get users")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def get_user(self, login: str) -> User:
        """Get a single user by login.

        Args:
            login: User login identifier

        Returns:
            User: User details

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If user not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_login = quote_plus(login)
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/users/{encoded_login}")

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return User.model_validate(data)
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to get user '{login}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def create_user(self, login: str, data: "UserCreate | dict") -> User:
        """Create a user (PUT — idempotent).

        Args:
            login: User login identifier
            data: User data as UserCreate model or dict

        Returns:
            User: Created user details

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCConflictError: If user already exists (409)
            OFSCValidationError: If data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        if isinstance(data, dict):
            data = UserCreate.model_validate(data)
        body = data.model_dump(exclude_none=True)

        encoded_login = quote_plus(login)
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/users/{encoded_login}")

        try:
            response = await self._client.put(url, headers=self.headers, json=body)
            response.raise_for_status()
            return User.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to create user '{login}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def update_user(self, login: str, data: dict) -> User:
        """Update a user (PATCH — partial update).

        Args:
            login: User login identifier
            data: Partial user data to update

        Returns:
            User: Updated user details

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If user not found (404)
            OFSCValidationError: If data is invalid (400/422)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_login = quote_plus(login)
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/users/{encoded_login}")

        try:
            response = await self._client.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
            return User.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to update user '{login}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_user(self, login: str) -> None:
        """Delete a user.

        Args:
            login: User login identifier

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If user not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_login = quote_plus(login)
        url = urljoin(self.baseUrl, f"/rest/ofscCore/v1/users/{encoded_login}")

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(e, f"Failed to delete user '{login}'")
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # region File Properties

    async def get_user_property(self, login: str, property_label: str) -> bytes:
        """Get a binary file property for a user.

        Args:
            login: User login identifier
            property_label: Property label (e.g., 'photo')

        Returns:
            bytes: Binary content of the property

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If user or property not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_login = quote_plus(login)
        encoded_label = quote_plus(property_label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/users/{encoded_login}/{encoded_label}"
        )
        headers = {**self.headers, "Accept": "application/octet-stream"}

        try:
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()
            return response.content
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get property '{property_label}' for user '{login}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def set_user_property(
        self,
        login: str,
        property_label: str,
        content: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
    ) -> None:
        """Upload a binary file property for a user.

        Args:
            login: User login identifier
            property_label: Property label (e.g., 'photo')
            content: Binary content to upload
            filename: Filename for the Content-Disposition header
            content_type: MIME type of the content (default: application/octet-stream)

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If user not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_login = quote_plus(login)
        encoded_label = quote_plus(property_label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/users/{encoded_login}/{encoded_label}"
        )
        # Override Content-Type for binary upload
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
            self._handle_http_error(
                e, f"Failed to set property '{property_label}' for user '{login}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_user_property(self, login: str, property_label: str) -> None:
        """Delete a binary file property for a user.

        Args:
            login: User login identifier
            property_label: Property label to delete

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If user or property not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_login = quote_plus(login)
        encoded_label = quote_plus(property_label)
        url = urljoin(
            self.baseUrl, f"/rest/ofscCore/v1/users/{encoded_login}/{encoded_label}"
        )

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to delete property '{property_label}' for user '{login}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # region Collaboration Groups

    async def get_user_collab_groups(self, login: str) -> CollaborationGroupsResponse:
        """Get collaboration groups for a user.

        Args:
            login: User login identifier

        Returns:
            CollaborationGroupsResponse: List of collaboration groups

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If user not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_login = quote_plus(login)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/users/{encoded_login}/collaborationGroups",
        )

        try:
            response = await self._client.get(url, headers=self.headers)
            response.raise_for_status()
            return CollaborationGroupsResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to get collaboration groups for user '{login}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def set_user_collab_groups(
        self, login: str, groups: list[str]
    ) -> CollaborationGroupsResponse:
        """Set collaboration groups for a user (POST — replaces all groups).

        Args:
            login: User login identifier
            groups: List of group names to assign

        Returns:
            CollaborationGroupsResponse: Updated list of collaboration groups

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If user not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_login = quote_plus(login)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/users/{encoded_login}/collaborationGroups",
        )
        body = {"items": [{"name": g} for g in groups]}

        try:
            response = await self._client.post(url, headers=self.headers, json=body)
            response.raise_for_status()
            return CollaborationGroupsResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to set collaboration groups for user '{login}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    async def delete_user_collab_groups(self, login: str) -> None:
        """Delete all collaboration groups for a user.

        Args:
            login: User login identifier

        Raises:
            OFSCAuthenticationError: If authentication fails (401)
            OFSCAuthorizationError: If authorization fails (403)
            OFSCNotFoundError: If user not found (404)
            OFSCApiError: For other API errors
            OFSCNetworkError: For network/transport errors
        """
        encoded_login = quote_plus(login)
        url = urljoin(
            self.baseUrl,
            f"/rest/ofscCore/v1/users/{encoded_login}/collaborationGroups",
        )

        try:
            response = await self._client.delete(url, headers=self.headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_http_error(
                e, f"Failed to delete collaboration groups for user '{login}'"
            )
            raise
        except httpx.TransportError as e:
            raise OFSCNetworkError(f"Network error: {str(e)}") from e

    # endregion

    # endregion
