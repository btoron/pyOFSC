import logging
from typing import TYPE_CHECKING

import httpx

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from ofsc.models.core import (
    Activity, ActivityListResponse, BulkUpdateRequest, BulkUpdateResponse, 
    Resource, ResourceListResponse, SubscriptionList, UserListResponse
)

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

    async def get_activities(
        self,
        resources: List[str],
        dateFrom: Optional[date] = None,
        dateTo: Optional[date] = None,
        includeChildren: str = "all",
        q: Optional[str] = None,
        fields: Optional[List[str]] = None,
        includeNonScheduled: bool = False,
        offset: int = 0,
        limit: int = 100,
    ) -> ActivityListResponse:
        """
        Get activities from the OFS Core API.

        Args:
            resources: List of resource IDs to retrieve activities for (required)
            dateFrom: Start date for activities (YYYY-MM-DD format)
            dateTo: End date for activities (YYYY-MM-DD format)
            includeChildren: Include subordinate resources ("none", "immediate", "all")
            q: Filter expression for activities
            fields: List of fields to return in response
            includeNonScheduled: Whether to include non-scheduled activities
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 100000)

        Returns:
            ActivityListResponse: Paginated list of activities
        """
        # Validate parameters internally
        class GetActivitiesParams(BaseModel):
            resources: List[str] = Field(min_length=1)
            dateFrom: Optional[date] = None
            dateTo: Optional[date] = None
            includeChildren: str = Field(default="all")
            q: Optional[str] = None
            fields: Optional[List[str]] = None
            includeNonScheduled: bool = False
            offset: int = Field(ge=0, default=0)
            limit: int = Field(ge=1, le=100000, default=100)
            
            @field_validator("includeChildren")
            @classmethod
            def validate_include_children(cls, v):
                if v not in ["none", "immediate", "all"]:
                    raise ValueError("includeChildren must be 'none', 'immediate', or 'all'")
                return v
                
            @field_validator("dateTo")
            @classmethod
            def validate_dates(cls, v, values):
                if v and not values.data.get("dateFrom"):
                    raise ValueError("dateFrom must be specified when dateTo is provided")
                return v

        # Validate
        params_model = GetActivitiesParams(
            resources=resources,
            dateFrom=dateFrom,
            dateTo=dateTo,
            includeChildren=includeChildren,
            q=q,
            fields=fields,
            includeNonScheduled=includeNonScheduled,
            offset=offset,
            limit=limit,
        )

        # Build query parameters
        params = {
            "resources": ",".join(params_model.resources),
            "includeChildren": params_model.includeChildren,
            "offset": params_model.offset,
            "limit": params_model.limit,
        }
        
        if params_model.dateFrom:
            params["dateFrom"] = params_model.dateFrom.isoformat()
        if params_model.dateTo:
            params["dateTo"] = params_model.dateTo.isoformat()
        if params_model.q:
            params["q"] = params_model.q
        if params_model.fields:
            params["fields"] = ",".join(params_model.fields)
        if params_model.includeNonScheduled:
            params["includeNonScheduled"] = "true"

        endpoint = "/rest/ofscCore/v1/activities"
        logging.info(f"Fetching activities from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint, params=params)
        return ActivityListResponse.from_response(response)

    async def create_activity(self, activity_data: dict) -> Activity:
        """
        Create a new activity in the OFS Core API.

        Args:
            activity_data: Dictionary containing activity properties
                Common fields include:
                - activityType: Type of activity (required)
                - date: Date for scheduling (YYYY-MM-DD format)
                - resourceId: Resource to assign to
                - customerEmail: Customer email
                - And many other custom properties

        Returns:
            Activity: The created activity
        """
        endpoint = "/rest/ofscCore/v1/activities"
        logging.info(f"Creating activity at endpoint: {endpoint}")
        
        response: "Response" = await self.client.post(endpoint, json=activity_data)
        return Activity.from_response(response)

    async def get_activity(self, activity_id: int) -> Activity:
        """
        Get a specific activity by ID from the OFS Core API.

        Args:
            activity_id: The unique identifier of the activity

        Returns:
            Activity: The activity details
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}"
        logging.info(f"Fetching activity from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return Activity.from_response(response)

    async def update_activity(self, activity_id: int, activity_data: dict) -> Activity:
        """
        Update an existing activity in the OFS Core API.

        Args:
            activity_id: The unique identifier of the activity
            activity_data: Dictionary containing activity properties to update

        Returns:
            Activity: The updated activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}"
        logging.info(f"Updating activity at endpoint: {endpoint}")
        
        response: "Response" = await self.client.patch(endpoint, json=activity_data)
        return Activity.from_response(response)

    async def delete_activity(self, activity_id: int) -> None:
        """
        Delete an activity from the OFS Core API.

        Args:
            activity_id: The unique identifier of the activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}"
        logging.info(f"Deleting activity at endpoint: {endpoint}")
        
        response: "Response" = await self.client.delete(endpoint)
        # DELETE typically returns 204 No Content on success
        if response.status_code not in [200, 204]:
            raise ValueError(f"Failed to delete activity {activity_id}: {response.status_code}")

    async def search_activities(self, **params) -> ActivityListResponse:
        """
        Search activities using the custom search endpoint.

        Args:
            **params: Search parameters (varies based on OFS configuration)
                Common parameters may include:
                - fields: List of fields to return
                - offset: Starting record offset
                - limit: Maximum records to return
                - Various filter parameters

        Returns:
            ActivityListResponse: Search results
        """
        endpoint = "/rest/ofscCore/v1/activities/custom-actions/search"
        logging.info(f"Searching activities at endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint, params=params)
        return ActivityListResponse.from_response(response)

    async def start_activity(self, activity_id: int) -> Activity:
        """
        Start an activity (change status to 'started').

        Args:
            activity_id: The unique identifier of the activity

        Returns:
            Activity: The updated activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/custom-actions/start"
        logging.info(f"Starting activity at endpoint: {endpoint}")
        
        response: "Response" = await self.client.post(endpoint)
        return Activity.from_response(response)

    async def complete_activity(self, activity_id: int) -> Activity:
        """
        Complete an activity (change status to 'completed').

        Args:
            activity_id: The unique identifier of the activity

        Returns:
            Activity: The updated activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/custom-actions/complete"
        logging.info(f"Completing activity at endpoint: {endpoint}")
        
        response: "Response" = await self.client.post(endpoint)
        return Activity.from_response(response)

    async def cancel_activity(self, activity_id: int) -> Activity:
        """
        Cancel an activity (change status to 'cancelled').

        Args:
            activity_id: The unique identifier of the activity

        Returns:
            Activity: The updated activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/custom-actions/cancel"
        logging.info(f"Cancelling activity at endpoint: {endpoint}")
        
        response: "Response" = await self.client.post(endpoint)
        return Activity.from_response(response)

    async def bulk_update_activities(self, bulk_data: BulkUpdateRequest) -> BulkUpdateResponse:
        """
        Perform bulk update operations on multiple activities.

        Args:
            bulk_data: BulkUpdateRequest containing the activities to update

        Returns:
            BulkUpdateResponse: Results of the bulk operation
        """
        endpoint = "/rest/ofscCore/v1/activities/custom-actions/bulkUpdate"
        logging.info(f"Bulk updating activities at endpoint: {endpoint}")
        
        # Convert Pydantic model to dict for JSON serialization
        request_data = bulk_data.model_dump(exclude_none=True)
        
        response: "Response" = await self.client.post(endpoint, json=request_data)
        return BulkUpdateResponse.from_response(response)

    # Resource Management
    
    async def get_resources(
        self,
        offset: int = 0,
        limit: int = 100,
        fields: Optional[List[str]] = None,
    ) -> ResourceListResponse:
        """
        Get resources from the OFS Core API.

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100)
            fields: List of fields to return in response

        Returns:
            ResourceListResponse: Paginated list of resources
        """
        endpoint = "/rest/ofscCore/v1/resources"
        
        # Build query parameters
        params = {"offset": offset, "limit": limit}
        if fields:
            params["fields"] = ",".join(fields)
            
        logging.info(f"Fetching resources from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint, params=params)
        return ResourceListResponse.from_response(response)

    async def get_resource(
        self,
        resource_id: str,
        inventories: bool = False,
        workSkills: bool = False,
        workZones: bool = False,
        workSchedules: bool = False,
    ) -> Resource:
        """
        Get a specific resource by ID from the OFS Core API.

        Args:
            resource_id: The unique identifier of the resource
            inventories: Include inventory information
            workSkills: Include work skills information
            workZones: Include work zones information
            workSchedules: Include work schedules information

        Returns:
            Resource: The resource details
        """
        if not resource_id or not isinstance(resource_id, str):
            raise ValueError("resource_id must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/resources/{resource_id}"
        
        # Build query parameters
        params = {}
        if inventories:
            params["inventories"] = "true"
        if workSkills:
            params["workSkills"] = "true"
        if workZones:
            params["workZones"] = "true"
        if workSchedules:
            params["workSchedules"] = "true"
            
        logging.info(f"Fetching resource from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint, params=params)
        return Resource.from_response(response)

    async def update_resource(self, resource_id: str, resource_data: dict) -> Resource:
        """
        Update an existing resource in the OFS Core API.

        Args:
            resource_id: The unique identifier of the resource
            resource_data: Dictionary containing resource properties to update

        Returns:
            Resource: The updated resource
        """
        if not resource_id or not isinstance(resource_id, str):
            raise ValueError("resource_id must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/resources/{resource_id}"
        logging.info(f"Updating resource at endpoint: {endpoint}")
        
        response: "Response" = await self.client.patch(endpoint, json=resource_data)
        return Resource.from_response(response)
