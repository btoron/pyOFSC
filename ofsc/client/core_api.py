import logging
from typing import TYPE_CHECKING

import httpx

from ofsc.models.core import SubscriptionList, UserListResponse

if TYPE_CHECKING:
    from httpx import Response


class OFSCoreAPI:
    """
    Interface for the OFS Core API (async-only).
    This class provides async methods to interact with the core functionalities of the OFS system.
    
    All methods are async and must be awaited.
    """

    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        logging.debug(
            f"OFSCoreAPI initialized with async client: {self.client} (base_url: {self.client.base_url})"
        )

    async def get_subscriptions(self, allSubscriptions: bool = False) -> SubscriptionList:
        """
        Get subscriptions from the OFS Core API.

        Args:
            allSubscriptions (bool): If True, fetch all subscriptions. Defaults to False.

        Returns:
            SubscriptionList: A list of subscriptions.
        """
        endpoint = "/rest/ofscCore/v1/events/subscriptions"
        logging.info(
            f"Fetching subscriptions from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )
        params = {"all": str(allSubscriptions).lower()} if allSubscriptions else {}

        response: "Response" = await self.client.get(endpoint, params=params)
        return SubscriptionList.from_response(response)

    async def get_users(self, offset: int = 0, limit: int = 100) -> UserListResponse:
        """
        Get users from the OFS Core API.

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100)

        Returns:
            UserListResponse: The response object containing user data.
        """
        endpoint = "/rest/ofscCore/v1/users"
        params = {"offset": offset, "limit": limit}
        logging.info(
            f"Fetching users from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return UserListResponse.from_response(response)
