import logging

import httpx

from ofsc.models.core import SubscriptionList, UserListResponse


class OFSCoreAPI:
    """
    Interface for the OFS Core API.
    This class provides methods to interact with the core functionalities of the OFS system.
    """

    def __init__(self, client):
        self.client = client
        self._is_async = isinstance(client, httpx.AsyncClient)
        logging.debug(
            f"OFSCoreAPI initialized with client: {self.client} (async: {self._is_async} base_url: {self.client.base_url})"
        )

    async def get_subscriptions(
        self, allSubscriptions: bool = False
    ) -> SubscriptionList:
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

        if self._is_async:
            response = await self.client.get(endpoint, params=params)
        else:
            response = self.client.get(endpoint, params=params)
        return SubscriptionList.from_response(response)

    async def get_users(self, offset: int = 0, limit: int = 100) -> UserListResponse:
        """
        Get users from the OFS Core API.

        Returns:
            UsersList: The response object containing user data.
        """
        endpoint = "/rest/ofscCore/v1/users"
        params = {"offset": offset, "limit": limit}
        logging.info(
            f"Fetching users from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        if self._is_async:
            response = await self.client.get(endpoint, params=params)
        else:
            response = self.client.get(endpoint, params=params)
        return UserListResponse.from_response(response)
