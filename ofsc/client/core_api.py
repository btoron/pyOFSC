import logging
from typing import TYPE_CHECKING

import httpx

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from ofsc.models.core import (
    Activity, ActivityCapacityCategory, ActivityCapacityCategoryListResponse,
    ActivityCustomerInventory, ActivityCustomerInventoryListResponse,
    ActivityDeinstalledInventory, ActivityDeinstalledInventoryListResponse,
    ActivityInstalledInventory, ActivityInstalledInventoryListResponse,
    ActivityLink, ActivityLinkListResponse, ActivityLinkType,
    ActivityListResponse, ActivityMoveRequest, ActivityMoveResponse,
    ActivityMultidaySegment, ActivityMultidaySegmentListResponse,
    ActivityProperty, ActivityRequiredInventory, ActivityRequiredInventoryListResponse,
    ActivityResourcePreference, ActivityResourcePreferenceListResponse,
    ActivitySubmittedForm, ActivitySubmittedFormListResponse, BulkUpdateRequest, 
    BulkUpdateResponse, DailyExtractFiles, DailyExtractFolders, Inventory, 
    InventoryListResponse, Resource, ResourceInventory, ResourceInventoryListResponse, 
    ResourceListResponse, ResourceUsersListResponse, ResourceWorkScheduleResponse, 
    ResourceWorkSkill, ResourceWorkSkillListResponse, ResourceWorkZone, 
    ResourceWorkZoneListResponse, SubscriptionList, User, UserListResponse
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

    # Daily Extract API
    
    async def get_daily_extract_dates(self) -> DailyExtractFolders:
        """
        Get available daily extract dates from the OFS Core API.

        Returns:
            DailyExtractFolders: Available extract date folders
        """
        endpoint = "/rest/ofscCore/v1/folders/dailyExtract/folders"
        logging.info(f"Fetching daily extract dates from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return DailyExtractFolders.from_response(response)

    async def get_daily_extract_files(self, extract_date: str) -> DailyExtractFiles:
        """
        Get available files for a specific daily extract date.

        Args:
            extract_date: Date in YYYY-MM-DD format

        Returns:
            DailyExtractFiles: Available files for the specified date
        """
        if not extract_date or not isinstance(extract_date, str):
            raise ValueError("extract_date must be a non-empty string in YYYY-MM-DD format")
            
        endpoint = f"/rest/ofscCore/v1/folders/dailyExtract/folders/{extract_date}/files"
        logging.info(f"Fetching daily extract files from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return DailyExtractFiles.from_response(response)

    async def get_daily_extract_file(
        self, 
        extract_date: str, 
        filename: str, 
        media_type: str = "application/octet-stream"
    ) -> bytes:
        """
        Download a specific daily extract file.

        Args:
            extract_date: Date in YYYY-MM-DD format
            filename: Name of the file to download
            media_type: Media type for the response (default: application/octet-stream)

        Returns:
            bytes: The file content as bytes
        """
        if not extract_date or not isinstance(extract_date, str):
            raise ValueError("extract_date must be a non-empty string in YYYY-MM-DD format")
        if not filename or not isinstance(filename, str):
            raise ValueError("filename must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/folders/dailyExtract/folders/{extract_date}/files/{filename}"
        
        # Set Accept header for media type
        headers = {"Accept": media_type}
        
        logging.info(f"Downloading daily extract file from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint, headers=headers)
        return response.content

    # User Management (Extended)
    
    async def get_user(self, login: str) -> User:
        """
        Get a specific user by login from the OFS Core API.

        Args:
            login: The user's login identifier

        Returns:
            User: The user details
        """
        if not login or not isinstance(login, str):
            raise ValueError("login must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/users/{login}"
        logging.info(f"Fetching user from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return User.from_response(response)

    async def create_user(self, login: str, user_data: dict) -> User:
        """
        Create a new user in the OFS Core API.

        Args:
            login: The user's login identifier
            user_data: Dictionary containing user properties

        Returns:
            User: The created user
        """
        if not login or not isinstance(login, str):
            raise ValueError("login must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/users/{login}"
        logging.info(f"Creating user at endpoint: {endpoint}")
        
        response: "Response" = await self.client.put(endpoint, json=user_data)
        return User.from_response(response)

    async def update_user(self, login: str, user_data: dict) -> User:
        """
        Update an existing user in the OFS Core API.

        Args:
            login: The user's login identifier
            user_data: Dictionary containing user properties to update

        Returns:
            User: The updated user
        """
        if not login or not isinstance(login, str):
            raise ValueError("login must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/users/{login}"
        logging.info(f"Updating user at endpoint: {endpoint}")
        
        response: "Response" = await self.client.patch(endpoint, json=user_data)
        return User.from_response(response)

    async def delete_user(self, login: str) -> None:
        """
        Delete a user from the OFS Core API.

        Args:
            login: The user's login identifier
        """
        if not login or not isinstance(login, str):
            raise ValueError("login must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/users/{login}"
        logging.info(f"Deleting user at endpoint: {endpoint}")
        
        response: "Response" = await self.client.delete(endpoint)
        if response.status_code not in [200, 204]:
            raise ValueError(f"Failed to delete user {login}: {response.status_code}")

    # Resource Management (Extended)
    
    async def get_resource_users(self, resource_id: str) -> ResourceUsersListResponse:
        """
        Get users associated with a specific resource.

        Args:
            resource_id: The unique identifier of the resource

        Returns:
            ResourceUsersListResponse: List of users associated with the resource
        """
        if not resource_id or not isinstance(resource_id, str):
            raise ValueError("resource_id must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/resources/{resource_id}/users"
        logging.info(f"Fetching resource users from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return ResourceUsersListResponse.from_response(response)

    async def set_resource_users(self, resource_id: str, user_logins: List[str]) -> ResourceUsersListResponse:
        """
        Set users associated with a specific resource.

        Args:
            resource_id: The unique identifier of the resource
            user_logins: List of user login identifiers to associate

        Returns:
            ResourceUsersListResponse: Updated list of users associated with the resource
        """
        if not resource_id or not isinstance(resource_id, str):
            raise ValueError("resource_id must be a non-empty string")
        if not user_logins or not isinstance(user_logins, list):
            raise ValueError("user_logins must be a non-empty list")
            
        endpoint = f"/rest/ofscCore/v1/resources/{resource_id}/users"
        logging.info(f"Setting resource users at endpoint: {endpoint}")
        
        # The API expects the user logins in a specific format
        request_data = {"users": user_logins}
        
        response: "Response" = await self.client.put(endpoint, json=request_data)
        return ResourceUsersListResponse.from_response(response)

    async def delete_resource_users(self, resource_id: str) -> None:
        """
        Remove all users associated with a specific resource.

        Args:
            resource_id: The unique identifier of the resource
        """
        if not resource_id or not isinstance(resource_id, str):
            raise ValueError("resource_id must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/resources/{resource_id}/users"
        logging.info(f"Deleting resource users at endpoint: {endpoint}")
        
        response: "Response" = await self.client.delete(endpoint)
        if response.status_code not in [200, 204]:
            raise ValueError(f"Failed to delete resource users for {resource_id}: {response.status_code}")

    async def get_resource_work_schedules(
        self, 
        resource_id: str, 
        actual_date: Optional[date] = None
    ) -> ResourceWorkScheduleResponse:
        """
        Get work schedules for a specific resource.

        Args:
            resource_id: The unique identifier of the resource
            actual_date: Specific date to get schedules for (YYYY-MM-DD format)

        Returns:
            ResourceWorkScheduleResponse: Work schedules for the resource
        """
        if not resource_id or not isinstance(resource_id, str):
            raise ValueError("resource_id must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/resources/{resource_id}/workSchedules"
        
        params = {}
        if actual_date:
            params["actualDate"] = actual_date.isoformat()
            
        logging.info(f"Fetching resource work schedules from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint, params=params)
        return ResourceWorkScheduleResponse.from_response(response)

    async def get_resource_descendants(
        self,
        resource_id: str,
        resource_fields: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 100,
        inventories: bool = False,
        work_skills: bool = False,
        work_zones: bool = False,
        work_schedules: bool = False,
    ) -> ResourceListResponse:
        """
        Get descendant resources for a specific resource.

        Args:
            resource_id: The unique identifier of the parent resource
            resource_fields: List of resource fields to return
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100)
            inventories: Include inventory information
            work_skills: Include work skills information
            work_zones: Include work zones information
            work_schedules: Include work schedules information

        Returns:
            ResourceListResponse: List of descendant resources
        """
        if not resource_id or not isinstance(resource_id, str):
            raise ValueError("resource_id must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/resources/{resource_id}/descendants"
        
        # Build query parameters
        params = {"offset": offset, "limit": limit}
        
        if resource_fields:
            params["resourceFields"] = ",".join(resource_fields)
        if inventories:
            params["inventories"] = "true"
        if work_skills:
            params["workSkills"] = "true"
        if work_zones:
            params["workZones"] = "true"
        if work_schedules:
            params["workSchedules"] = "true"
            
        logging.info(f"Fetching resource descendants from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint, params=params)
        return ResourceListResponse.from_response(response)

    # Inventory Management

    async def create_inventory(self, inventory_data: dict) -> Inventory:
        """
        Create a new inventory item in the OFS Core API.

        Args:
            inventory_data: Dictionary containing inventory properties
                Required fields typically include:
                - inventoryType: Type of inventory item (required)
                - serialNumber: Serial number or identifier
                - model: Model information
                - quantity: Number of items
                - status: Current status

        Returns:
            Inventory: The created inventory item
        """
        endpoint = "/rest/ofscCore/v1/inventories"
        logging.info(f"Creating inventory item at endpoint: {endpoint}")
        
        response: "Response" = await self.client.post(endpoint, json=inventory_data)
        return Inventory.from_response(response)

    async def get_inventory(self, inventory_id: int) -> Inventory:
        """
        Get a specific inventory item by ID from the OFS Core API.

        Args:
            inventory_id: The unique identifier of the inventory item

        Returns:
            Inventory: The inventory item details
        """
        # Validate parameter
        if not isinstance(inventory_id, int) or inventory_id <= 0:
            raise ValueError("inventory_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/inventories/{inventory_id}"
        logging.info(f"Fetching inventory item from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return Inventory.from_response(response)

    async def update_inventory(self, inventory_id: int, inventory_data: dict) -> Inventory:
        """
        Update an existing inventory item in the OFS Core API.

        Args:
            inventory_id: The unique identifier of the inventory item
            inventory_data: Dictionary containing inventory properties to update

        Returns:
            Inventory: The updated inventory item
        """
        # Validate parameter
        if not isinstance(inventory_id, int) or inventory_id <= 0:
            raise ValueError("inventory_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/inventories/{inventory_id}"
        logging.info(f"Updating inventory item at endpoint: {endpoint}")
        
        response: "Response" = await self.client.patch(endpoint, json=inventory_data)
        return Inventory.from_response(response)

    async def get_resource_inventories(self, resource_id: str) -> ResourceInventoryListResponse:
        """
        Get inventory items assigned to a specific resource.

        Args:
            resource_id: The unique identifier of the resource

        Returns:
            ResourceInventoryListResponse: List of inventory items assigned to the resource
        """
        if not resource_id or not isinstance(resource_id, str):
            raise ValueError("resource_id must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/resources/{resource_id}/inventories"
        logging.info(f"Fetching resource inventories from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return ResourceInventoryListResponse.from_response(response)

    async def assign_inventory_to_resource(
        self, 
        resource_id: str, 
        inventory_data: dict
    ) -> ResourceInventory:
        """
        Assign inventory items to a specific resource.

        Args:
            resource_id: The unique identifier of the resource
            inventory_data: Dictionary containing inventory assignment data
                Typical fields include:
                - inventoryId: ID of inventory item to assign
                - inventoryType: Type of inventory
                - quantity: Number of items to assign
                - serialNumber: Serial number if applicable

        Returns:
            ResourceInventory: The assigned inventory item
        """
        if not resource_id or not isinstance(resource_id, str):
            raise ValueError("resource_id must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/resources/{resource_id}/inventories"
        logging.info(f"Assigning inventory to resource at endpoint: {endpoint}")
        
        response: "Response" = await self.client.post(endpoint, json=inventory_data)
        return ResourceInventory.from_response(response)

    # Activity Property Management

    async def get_activity_property(self, activity_id: int, property_label: str) -> ActivityProperty:
        """
        Get a specific property value for an activity.

        Args:
            activity_id: The unique identifier of the activity
            property_label: The label/name of the property to retrieve

        Returns:
            ActivityProperty: The property value
        """
        # Validate parameters
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
        if not property_label or not isinstance(property_label, str):
            raise ValueError("property_label must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/{property_label}"
        logging.info(f"Fetching activity property from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return ActivityProperty.from_response(response)

    async def set_activity_property(
        self, 
        activity_id: int, 
        property_label: str, 
        property_value: Any
    ) -> ActivityProperty:
        """
        Set a specific property value for an activity.

        Args:
            activity_id: The unique identifier of the activity
            property_label: The label/name of the property to set
            property_value: The value to set for the property

        Returns:
            ActivityProperty: The updated property
        """
        # Validate parameters
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
        if not property_label or not isinstance(property_label, str):
            raise ValueError("property_label must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/{property_label}"
        logging.info(f"Setting activity property at endpoint: {endpoint}")
        
        # The property value is sent as the request body
        property_data = {"value": property_value}
        
        response: "Response" = await self.client.put(endpoint, json=property_data)
        return ActivityProperty.from_response(response)

    async def get_activity_submitted_forms(self, activity_id: int) -> ActivitySubmittedFormListResponse:
        """
        Get submitted forms for a specific activity.

        Args:
            activity_id: The unique identifier of the activity

        Returns:
            ActivitySubmittedFormListResponse: List of submitted forms for the activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/submittedForms"
        logging.info(f"Fetching activity submitted forms from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return ActivitySubmittedFormListResponse.from_response(response)

    # Resource Configuration Management

    async def get_resource_work_skills(self, resource_id: str) -> ResourceWorkSkillListResponse:
        """
        Get work skills associated with a specific resource.

        Args:
            resource_id: The unique identifier of the resource

        Returns:
            ResourceWorkSkillListResponse: List of work skills assigned to the resource
        """
        if not resource_id or not isinstance(resource_id, str):
            raise ValueError("resource_id must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/resources/{resource_id}/workSkills"
        logging.info(f"Fetching resource work skills from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return ResourceWorkSkillListResponse.from_response(response)

    async def add_resource_work_skills(
        self, 
        resource_id: str, 
        work_skills_data: List[dict]
    ) -> ResourceWorkSkillListResponse:
        """
        Add work skills to a specific resource.

        Args:
            resource_id: The unique identifier of the resource
            work_skills_data: List of work skill dictionaries to add
                Each dictionary should include:
                - workSkillLabel: Name/label of the work skill (required)
                - level: Skill level (optional)

        Returns:
            ResourceWorkSkillListResponse: Updated list of work skills
        """
        if not resource_id or not isinstance(resource_id, str):
            raise ValueError("resource_id must be a non-empty string")
        if not work_skills_data or not isinstance(work_skills_data, list):
            raise ValueError("work_skills_data must be a non-empty list")
            
        endpoint = f"/rest/ofscCore/v1/resources/{resource_id}/workSkills"
        logging.info(f"Adding work skills to resource at endpoint: {endpoint}")
        
        # The API expects work skills in a specific format
        request_data = {"workSkills": work_skills_data}
        
        response: "Response" = await self.client.post(endpoint, json=request_data)
        return ResourceWorkSkillListResponse.from_response(response)

    async def get_resource_work_zones(self, resource_id: str) -> ResourceWorkZoneListResponse:
        """
        Get work zones assigned to a specific resource.

        Args:
            resource_id: The unique identifier of the resource

        Returns:
            ResourceWorkZoneListResponse: List of work zones assigned to the resource
        """
        if not resource_id or not isinstance(resource_id, str):
            raise ValueError("resource_id must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/resources/{resource_id}/workZones"
        logging.info(f"Fetching resource work zones from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return ResourceWorkZoneListResponse.from_response(response)

    async def assign_resource_work_zones(
        self, 
        resource_id: str, 
        work_zones_data: List[dict]
    ) -> ResourceWorkZoneListResponse:
        """
        Assign work zones to a specific resource.

        Args:
            resource_id: The unique identifier of the resource
            work_zones_data: List of work zone dictionaries to assign
                Each dictionary should include:
                - workZoneLabel: Name/label of the work zone (required)

        Returns:
            ResourceWorkZoneListResponse: Updated list of work zones
        """
        if not resource_id or not isinstance(resource_id, str):
            raise ValueError("resource_id must be a non-empty string")
        if not work_zones_data or not isinstance(work_zones_data, list):
            raise ValueError("work_zones_data must be a non-empty list")
            
        endpoint = f"/rest/ofscCore/v1/resources/{resource_id}/workZones"
        logging.info(f"Assigning work zones to resource at endpoint: {endpoint}")
        
        # The API expects work zones in a specific format
        request_data = {"workZones": work_zones_data}
        
        response: "Response" = await self.client.post(endpoint, json=request_data)
        return ResourceWorkZoneListResponse.from_response(response)

    # Activity Advanced Operations (Batch 1)

    async def get_activity_multiday_segments(self, activity_id: int) -> ActivityMultidaySegmentListResponse:
        """
        Get multiday segments for a specific activity.

        Args:
            activity_id: The unique identifier of the activity

        Returns:
            ActivityMultidaySegmentListResponse: List of multiday segments for the activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/multidaySegments"
        logging.info(f"Fetching activity multiday segments from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return ActivityMultidaySegmentListResponse.from_response(response)

    async def delete_activity_property(self, activity_id: int, property_label: str) -> None:
        """
        Delete a specific property from an activity.

        Args:
            activity_id: The unique identifier of the activity
            property_label: The label/name of the property to delete
        """
        # Validate parameters
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
        if not property_label or not isinstance(property_label, str):
            raise ValueError("property_label must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/{property_label}"
        logging.info(f"Deleting activity property at endpoint: {endpoint}")
        
        response: "Response" = await self.client.delete(endpoint)
        # DELETE typically returns 204 No Content on success
        if response.status_code not in [200, 204]:
            raise ValueError(f"Failed to delete activity property {property_label}: {response.status_code}")

    async def get_activity_capacity_categories(self, activity_id: int) -> ActivityCapacityCategoryListResponse:
        """
        Get capacity categories associated with a specific activity.

        Args:
            activity_id: The unique identifier of the activity

        Returns:
            ActivityCapacityCategoryListResponse: List of capacity categories for the activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/capacityCategories"
        logging.info(f"Fetching activity capacity categories from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return ActivityCapacityCategoryListResponse.from_response(response)

    async def start_activity_prework(self, activity_id: int) -> Activity:
        """
        Start prework for an activity (change status to 'prework').

        Args:
            activity_id: The unique identifier of the activity

        Returns:
            Activity: The updated activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/custom-actions/startPrework"
        logging.info(f"Starting activity prework at endpoint: {endpoint}")
        
        response: "Response" = await self.client.post(endpoint)
        return Activity.from_response(response)

    async def reopen_activity(self, activity_id: int) -> Activity:
        """
        Reopen a completed or cancelled activity.

        Args:
            activity_id: The unique identifier of the activity

        Returns:
            Activity: The updated activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/custom-actions/reopen"
        logging.info(f"Reopening activity at endpoint: {endpoint}")
        
        response: "Response" = await self.client.post(endpoint)
        return Activity.from_response(response)

    async def delay_activity(self, activity_id: int, delay_data: Optional[dict] = None) -> Activity:
        """
        Delay an activity with optional delay information.

        Args:
            activity_id: The unique identifier of the activity
            delay_data: Optional dictionary containing delay information
                May include fields like:
                - delayReason: Reason for the delay
                - delayDuration: Duration of delay in minutes
                - newScheduledTime: New scheduled time

        Returns:
            Activity: The updated activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/custom-actions/delay"
        logging.info(f"Delaying activity at endpoint: {endpoint}")
        
        # Send delay data if provided, otherwise empty request
        request_data = delay_data if delay_data else {}
        
        response: "Response" = await self.client.post(endpoint, json=request_data)
        return Activity.from_response(response)

    async def set_activity_enroute(self, activity_id: int) -> Activity:
        """
        Set activity status to 'enroute' (technician is traveling to the location).

        Args:
            activity_id: The unique identifier of the activity

        Returns:
            Activity: The updated activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/custom-actions/enroute"
        logging.info(f"Setting activity enroute at endpoint: {endpoint}")
        
        response: "Response" = await self.client.post(endpoint)
        return Activity.from_response(response)

    # Resource Preferences & Requirements (Batch 2)

    async def set_activity_resource_preferences(
        self, 
        activity_id: int, 
        preferences_data: List[dict]
    ) -> ActivityResourcePreferenceListResponse:
        """
        Set resource preferences for a specific activity.

        Args:
            activity_id: The unique identifier of the activity
            preferences_data: List of resource preference dictionaries
                Each dictionary should include:
                - resourceId: ID of the resource (required)
                - preferenceType: Type of preference ("preferred", "required", "excluded")
                - priority: Priority level (optional)

        Returns:
            ActivityResourcePreferenceListResponse: Updated resource preferences
        """
        # Validate parameters
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
        if not preferences_data or not isinstance(preferences_data, list):
            raise ValueError("preferences_data must be a non-empty list")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/resourcePreferences"
        logging.info(f"Setting activity resource preferences at endpoint: {endpoint}")
        
        # The API expects preferences in a specific format
        request_data = {"resourcePreferences": preferences_data}
        
        response: "Response" = await self.client.put(endpoint, json=request_data)
        return ActivityResourcePreferenceListResponse.from_response(response)

    async def get_activity_resource_preferences(self, activity_id: int) -> ActivityResourcePreferenceListResponse:
        """
        Get resource preferences for a specific activity.

        Args:
            activity_id: The unique identifier of the activity

        Returns:
            ActivityResourcePreferenceListResponse: List of resource preferences
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/resourcePreferences"
        logging.info(f"Fetching activity resource preferences from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return ActivityResourcePreferenceListResponse.from_response(response)

    async def delete_activity_resource_preferences(self, activity_id: int) -> None:
        """
        Delete all resource preferences for a specific activity.

        Args:
            activity_id: The unique identifier of the activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/resourcePreferences"
        logging.info(f"Deleting activity resource preferences at endpoint: {endpoint}")
        
        response: "Response" = await self.client.delete(endpoint)
        if response.status_code not in [200, 204]:
            raise ValueError(f"Failed to delete resource preferences for activity {activity_id}: {response.status_code}")

    async def set_activity_required_inventories(
        self, 
        activity_id: int, 
        inventories_data: List[dict]
    ) -> ActivityRequiredInventoryListResponse:
        """
        Set required inventories for a specific activity.

        Args:
            activity_id: The unique identifier of the activity
            inventories_data: List of required inventory dictionaries
                Each dictionary should include:
                - inventoryType: Type of inventory required (required)
                - quantity: Number of items required (default: 1)
                - serialNumber: Specific serial number if required
                - model: Specific model if required

        Returns:
            ActivityRequiredInventoryListResponse: Updated required inventories
        """
        # Validate parameters
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
        if not inventories_data or not isinstance(inventories_data, list):
            raise ValueError("inventories_data must be a non-empty list")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/requiredInventories"
        logging.info(f"Setting activity required inventories at endpoint: {endpoint}")
        
        # The API expects inventories in a specific format
        request_data = {"requiredInventories": inventories_data}
        
        response: "Response" = await self.client.put(endpoint, json=request_data)
        return ActivityRequiredInventoryListResponse.from_response(response)

    async def get_activity_required_inventories(self, activity_id: int) -> ActivityRequiredInventoryListResponse:
        """
        Get required inventories for a specific activity.

        Args:
            activity_id: The unique identifier of the activity

        Returns:
            ActivityRequiredInventoryListResponse: List of required inventories
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/requiredInventories"
        logging.info(f"Fetching activity required inventories from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return ActivityRequiredInventoryListResponse.from_response(response)

    async def delete_activity_required_inventories(self, activity_id: int) -> None:
        """
        Delete all required inventories for a specific activity.

        Args:
            activity_id: The unique identifier of the activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/requiredInventories"
        logging.info(f"Deleting activity required inventories at endpoint: {endpoint}")
        
        response: "Response" = await self.client.delete(endpoint)
        if response.status_code not in [200, 204]:
            raise ValueError(f"Failed to delete required inventories for activity {activity_id}: {response.status_code}")

    # Activity Inventory Management (Batch 3)

    async def add_activity_customer_inventory(
        self, 
        activity_id: int, 
        inventory_data: dict
    ) -> ActivityCustomerInventory:
        """
        Add customer inventory to a specific activity.

        Args:
            activity_id: The unique identifier of the activity
            inventory_data: Dictionary containing customer inventory information
                Should include:
                - inventoryType: Type of inventory (required)
                - serialNumber: Serial number (optional)
                - model: Model information (optional)
                - quantity: Number of items (default: 1)
                - customerId: Customer identifier (optional)

        Returns:
            ActivityCustomerInventory: The added customer inventory
        """
        # Validate parameters
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
        if not inventory_data or not isinstance(inventory_data, dict):
            raise ValueError("inventory_data must be a non-empty dictionary")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/customerInventories"
        logging.info(f"Adding customer inventory to activity at endpoint: {endpoint}")
        
        response: "Response" = await self.client.post(endpoint, json=inventory_data)
        return ActivityCustomerInventory.from_response(response)

    async def get_activity_customer_inventories(self, activity_id: int) -> ActivityCustomerInventoryListResponse:
        """
        Get customer inventories associated with a specific activity.

        Args:
            activity_id: The unique identifier of the activity

        Returns:
            ActivityCustomerInventoryListResponse: List of customer inventories
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/customerInventories"
        logging.info(f"Fetching activity customer inventories from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return ActivityCustomerInventoryListResponse.from_response(response)

    async def get_activity_installed_inventories(self, activity_id: int) -> ActivityInstalledInventoryListResponse:
        """
        Get installed inventories for a specific activity.

        Args:
            activity_id: The unique identifier of the activity

        Returns:
            ActivityInstalledInventoryListResponse: List of installed inventories
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/installedInventories"
        logging.info(f"Fetching activity installed inventories from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return ActivityInstalledInventoryListResponse.from_response(response)

    async def get_activity_deinstalled_inventories(self, activity_id: int) -> ActivityDeinstalledInventoryListResponse:
        """
        Get deinstalled inventories for a specific activity.

        Args:
            activity_id: The unique identifier of the activity

        Returns:
            ActivityDeinstalledInventoryListResponse: List of deinstalled inventories
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/deinstalledInventories"
        logging.info(f"Fetching activity deinstalled inventories from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return ActivityDeinstalledInventoryListResponse.from_response(response)

    # Activity Relationships & Advanced Actions (Batch 4)

    async def get_activity_linked_activities(self, activity_id: int) -> ActivityLinkListResponse:
        """
        Get linked activities for a specific activity.

        Args:
            activity_id: The unique identifier of the activity

        Returns:
            ActivityLinkListResponse: List of linked activities
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/linkedActivities"
        logging.info(f"Fetching activity linked activities from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return ActivityLinkListResponse.from_response(response)

    async def delete_activity_linked_activities(self, activity_id: int) -> None:
        """
        Delete all linked activities for a specific activity.

        Args:
            activity_id: The unique identifier of the activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/linkedActivities"
        logging.info(f"Deleting activity linked activities at endpoint: {endpoint}")
        
        response: "Response" = await self.client.delete(endpoint)
        if response.status_code not in [200, 204]:
            raise ValueError(f"Failed to delete linked activities for activity {activity_id}: {response.status_code}")

    async def add_activity_linked_activities(
        self, 
        activity_id: int, 
        linked_activities_data: List[dict]
    ) -> ActivityLinkListResponse:
        """
        Add linked activities to a specific activity.

        Args:
            activity_id: The unique identifier of the activity
            linked_activities_data: List of linked activity dictionaries
                Each dictionary should include:
                - linkedActivityId: ID of the linked activity (required)
                - linkType: Type of link (required)
                - description: Description of the link (optional)

        Returns:
            ActivityLinkListResponse: Updated list of linked activities
        """
        # Validate parameters
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
        if not linked_activities_data or not isinstance(linked_activities_data, list):
            raise ValueError("linked_activities_data must be a non-empty list")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/linkedActivities"
        logging.info(f"Adding linked activities to activity at endpoint: {endpoint}")
        
        # The API expects linked activities in a specific format
        request_data = {"linkedActivities": linked_activities_data}
        
        response: "Response" = await self.client.post(endpoint, json=request_data)
        return ActivityLinkListResponse.from_response(response)

    async def delete_activity_link(
        self, 
        activity_id: int, 
        linked_activity_id: int, 
        link_type: str
    ) -> None:
        """
        Delete a specific link between two activities.

        Args:
            activity_id: The unique identifier of the main activity
            linked_activity_id: The unique identifier of the linked activity
            link_type: The type of link to delete
        """
        # Validate parameters
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
        if not isinstance(linked_activity_id, int) or linked_activity_id <= 0:
            raise ValueError("linked_activity_id must be a positive integer")
        if not link_type or not isinstance(link_type, str):
            raise ValueError("link_type must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/linkedActivities/{linked_activity_id}/linkTypes/{link_type}"
        logging.info(f"Deleting activity link at endpoint: {endpoint}")
        
        response: "Response" = await self.client.delete(endpoint)
        if response.status_code not in [200, 204]:
            raise ValueError(f"Failed to delete activity link: {response.status_code}")

    async def get_activity_link(
        self, 
        activity_id: int, 
        linked_activity_id: int, 
        link_type: str
    ) -> ActivityLink:
        """
        Get a specific link between two activities.

        Args:
            activity_id: The unique identifier of the main activity
            linked_activity_id: The unique identifier of the linked activity
            link_type: The type of link to retrieve

        Returns:
            ActivityLink: The activity link information
        """
        # Validate parameters
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
        if not isinstance(linked_activity_id, int) or linked_activity_id <= 0:
            raise ValueError("linked_activity_id must be a positive integer")
        if not link_type or not isinstance(link_type, str):
            raise ValueError("link_type must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/linkedActivities/{linked_activity_id}/linkTypes/{link_type}"
        logging.info(f"Fetching activity link from endpoint: {endpoint}")
        
        response: "Response" = await self.client.get(endpoint)
        return ActivityLink.from_response(response)

    async def set_activity_link(
        self, 
        activity_id: int, 
        linked_activity_id: int, 
        link_type: str,
        link_data: Optional[dict] = None
    ) -> ActivityLink:
        """
        Set/update a specific link between two activities.

        Args:
            activity_id: The unique identifier of the main activity
            linked_activity_id: The unique identifier of the linked activity
            link_type: The type of link to set
            link_data: Optional dictionary containing link properties

        Returns:
            ActivityLink: The updated activity link
        """
        # Validate parameters
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
        if not isinstance(linked_activity_id, int) or linked_activity_id <= 0:
            raise ValueError("linked_activity_id must be a positive integer")
        if not link_type or not isinstance(link_type, str):
            raise ValueError("link_type must be a non-empty string")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/linkedActivities/{linked_activity_id}/linkTypes/{link_type}"
        logging.info(f"Setting activity link at endpoint: {endpoint}")
        
        # Send link data if provided, otherwise empty request
        request_data = link_data if link_data else {}
        
        response: "Response" = await self.client.put(endpoint, json=request_data)
        return ActivityLink.from_response(response)

    async def stop_activity_travel(self, activity_id: int) -> Activity:
        """
        Stop travel for an activity (technician has stopped traveling).

        Args:
            activity_id: The unique identifier of the activity

        Returns:
            Activity: The updated activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/custom-actions/stopTravel"
        logging.info(f"Stopping activity travel at endpoint: {endpoint}")
        
        response: "Response" = await self.client.post(endpoint)
        return Activity.from_response(response)

    async def suspend_activity(self, activity_id: int, suspend_data: Optional[dict] = None) -> Activity:
        """
        Suspend an activity temporarily.

        Args:
            activity_id: The unique identifier of the activity
            suspend_data: Optional dictionary containing suspension information
                May include fields like:
                - suspendReason: Reason for suspension
                - suspendDuration: Duration of suspension
                - resumeTime: When to resume the activity

        Returns:
            Activity: The updated activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/custom-actions/suspend"
        logging.info(f"Suspending activity at endpoint: {endpoint}")
        
        # Send suspend data if provided, otherwise empty request
        request_data = suspend_data if suspend_data else {}
        
        response: "Response" = await self.client.post(endpoint, json=request_data)
        return Activity.from_response(response)

    async def move_activity(self, activity_id: int, move_data: dict) -> ActivityMoveResponse:
        """
        Move an activity to a different resource or time slot.

        Args:
            activity_id: The unique identifier of the activity
            move_data: Dictionary containing move parameters
                Should include:
                - targetResourceId: Target resource ID (optional)
                - targetDate: Target date (YYYY-MM-DD format, optional)
                - targetTime: Target time (HH:MM format, optional)
                - moveReason: Reason for the move (optional)
                - preserveTimeWindow: Whether to preserve time window (default: true)

        Returns:
            ActivityMoveResponse: Information about the move operation
        """
        # Validate parameters
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
        if not move_data or not isinstance(move_data, dict):
            raise ValueError("move_data must be a non-empty dictionary")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/custom-actions/move"
        logging.info(f"Moving activity at endpoint: {endpoint}")
        
        response: "Response" = await self.client.post(endpoint, json=move_data)
        return ActivityMoveResponse.from_response(response)

    async def mark_activity_not_done(self, activity_id: int, not_done_data: Optional[dict] = None) -> Activity:
        """
        Mark an activity as 'not done' with optional reason.

        Args:
            activity_id: The unique identifier of the activity
            not_done_data: Optional dictionary containing not done information
                May include fields like:
                - notDoneReason: Reason why activity was not completed
                - reschedule: Whether to reschedule the activity
                - newDate: New scheduled date if rescheduling

        Returns:
            Activity: The updated activity
        """
        # Validate parameter
        if not isinstance(activity_id, int) or activity_id <= 0:
            raise ValueError("activity_id must be a positive integer")
            
        endpoint = f"/rest/ofscCore/v1/activities/{activity_id}/custom-actions/notDone"
        logging.info(f"Marking activity not done at endpoint: {endpoint}")
        
        # Send not done data if provided, otherwise empty request
        request_data = not_done_data if not_done_data else {}
        
        response: "Response" = await self.client.post(endpoint, json=request_data)
        return Activity.from_response(response)
