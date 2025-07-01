"""Metadata API implementation for v3.0 OFSC async-only client architecture.

This module implements the Metadata API endpoints using the new v3.0 architecture with:
- httpx.AsyncClient for async-only operations
- Pydantic model responses
- Internal request parameter validation
- Fault tolerance (retry + circuit breaker)
"""

import logging
import urllib.parse
from typing import TYPE_CHECKING, List

import httpx
from pydantic import BaseModel, Field, ValidationError

from ofsc.exceptions import OFSValidationException
from ofsc.models.capacity import (
    CapacityArea,
    CapacityAreaCategoryListResponse,
    CapacityAreaListResponse,
    CapacityAreaOrganizationListResponse,
    CapacityAreaTimeIntervalListResponse,
    CapacityAreaTimeSlotListResponse,
    CapacityAreaWorkzoneListResponse,
    CapacityCategory,
    CapacityCategoryListResponse,
)
from ofsc.models.metadata import (
    ActivityType,
    ActivityTypeGroup,
    ActivityTypeGroupListResponse,
    ActivityTypeListResponse,
    Application,
    ApplicationListResponse,
    EnumerationValueList,
    InventoryType,
    InventoryTypeListResponse,
    Organization,
    OrganizationListResponse,
    Property,
    PropertyListResponse,
    ResourceTypeListResponse,
    TimeSlotListResponse,
    Workskill,
    WorkskillConditionListResponse,
    WorkSkillGroup,
    WorkSkillGroupListResponse,
    WorkskillListResponse,
    WorkzoneListResponse,
)

if TYPE_CHECKING:
    from httpx import Response

logger = logging.getLogger(__name__)


# Request validation models (internal use only)
class PaginationParams(BaseModel):
    """Internal validation for pagination parameters."""

    offset: int = Field(default=0, ge=0, description="Starting record offset")
    limit: int = Field(
        default=100, ge=1, le=1000, description="Maximum records to return"
    )


class LabelParam(BaseModel):
    """Internal validation for label parameters."""

    label: str = Field(
        min_length=1, max_length=255, description="Resource label identifier"
    )


class CapacityAreasParams(BaseModel):
    """Internal validation for capacity areas parameters."""

    expandParent: bool = Field(
        default=False, description="Expand parent area information"
    )
    fields: List[str] = Field(
        default=["label"], description="Fields to include in response"
    )
    activeOnly: bool = Field(default=False, description="Return only active areas")
    areasOnly: bool = Field(default=False, description="Return only area type entries")


class OFSMetadataAPI:
    """Metadata API client for async-only operations."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize the Metadata API client.

        Args:
            client: httpx AsyncClient instance with base_url and auth headers configured
        """
        self.client = client
        logging.debug(
            f"OFSMetadataAPI initialized with async client: {self.client} (base_url: {self.client.base_url})"
        )

    def _validate_params(self, model_class: type[BaseModel], **kwargs) -> dict:
        """Validate request parameters using Pydantic models.

        Args:
            model_class: Pydantic model class for validation
            **kwargs: Parameters to validate

        Returns:
            Validated parameters as dict

        Raises:
            OFSValidationException: If validation fails
        """
        try:
            validated = model_class(**kwargs)
            return validated.model_dump(exclude_none=True)
        except ValidationError as e:
            raise OFSValidationException(f"Parameter validation failed: {e}")

    # Properties API
    async def get_properties(
        self, offset: int = 0, limit: int = 100
    ) -> PropertyListResponse:
        """Get properties list.

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            PropertyListResponse response model with list of properties

        Raises:
            OFSValidationException: If parameters are invalid
        """
        # Validate parameters
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        endpoint = "/rest/ofscMetadata/v1/properties"
        logging.info(
            f"Fetching properties from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return PropertyListResponse.from_response(response)

    async def get_property(self, label: str) -> Property:
        """Get single property by label.

        Args:
            label: Property label identifier

        Returns:
            Property response model

        Raises:
            OFSValidationException: If label is invalid
        """
        # Validate parameters
        self._validate_params(LabelParam, label=label)

        endpoint = f"/rest/ofscMetadata/v1/properties/{label}"
        response: "Response" = await self.client.get(endpoint)
        return Property.from_response(response)

    # Work Skills API
    async def get_workskills(
        self, offset: int = 0, limit: int = 100
    ) -> WorkskillListResponse:
        """Get work skills list.

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            WorkskillListResponse response model with list of work skills
        """
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        endpoint = "/rest/ofscMetadata/v1/workSkills"
        logging.info(
            f"Fetching workskills from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return WorkskillListResponse.from_response(response)

    async def get_workskill(self, label: str) -> Workskill:
        """Get single work skill by label."""
        self._validate_params(LabelParam, label=label)

        endpoint = f"/rest/ofscMetadata/v1/workSkills/{label}"
        response: "Response" = await self.client.get(endpoint)
        return Workskill.from_response(response)

    # Activity Types API
    async def get_activity_types(
        self, offset: int = 0, limit: int = 100
    ) -> ActivityTypeListResponse:
        """Get activity types list."""
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        endpoint = "/rest/ofscMetadata/v1/activityTypes"
        response: "Response" = await self.client.get(endpoint, params=params)
        return ActivityTypeListResponse.from_response(response)

    async def get_activity_type(self, label: str) -> ActivityType:
        """Get single activity type by label."""
        self._validate_params(LabelParam, label=label)

        endpoint = f"/rest/ofscMetadata/v1/activityTypes/{label}"
        response: "Response" = await self.client.get(endpoint)
        return ActivityType.from_response(response)

    # Additional Metadata API endpoints
    async def get_enumeration_values(
        self, label: str, offset: int = 0, limit: int = 100
    ) -> EnumerationValueList:
        """Get enumeration values for a property."""
        self._validate_params(LabelParam, label=label)
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        endpoint = f"/rest/ofscMetadata/v1/properties/{label}/enumerationList"
        response: "Response" = await self.client.get(endpoint, params=params)
        return EnumerationValueList.from_response(response)

    # Resource Types API
    async def get_resource_types(self) -> ResourceTypeListResponse:
        """Get resource types list."""
        endpoint = "/rest/ofscMetadata/v1/resourceTypes"
        response: "Response" = await self.client.get(endpoint)
        return ResourceTypeListResponse.from_response(response)

    # Activity Type Groups API
    async def get_activity_type_groups(
        self, offset: int = 0, limit: int = 100
    ) -> ActivityTypeGroupListResponse:
        """Get activity type groups list."""
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        endpoint = "/rest/ofscMetadata/v1/activityTypeGroups"
        response: "Response" = await self.client.get(endpoint, params=params)
        return ActivityTypeGroupListResponse.from_response(response)

    async def get_activity_type_group(self, label: str) -> ActivityTypeGroup:
        """Get single activity type group by label."""
        self._validate_params(LabelParam, label=label)

        endpoint = f"/rest/ofscMetadata/v1/activityTypeGroups/{label}"
        response: "Response" = await self.client.get(endpoint)
        return ActivityTypeGroup.from_response(response)

    # Work Zones API
    async def get_workzones(
        self, offset: int = 0, limit: int = 100
    ) -> WorkzoneListResponse:
        """Get work zones list.

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            WorkzoneListResponse response model with list of work zones

        Raises:
            OFSValidationException: If parameters are invalid
        """
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        endpoint = "/rest/ofscMetadata/v1/workZones"
        logging.info(
            f"Fetching work zones from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return WorkzoneListResponse.from_response(response)

    # Work Skill Conditions API
    async def get_workskill_conditions(self) -> WorkskillConditionListResponse:
        """Get work skill conditions list.

        Returns:
            WorkskillConditionListResponse response model with work skill conditions
        """
        endpoint = "/rest/ofscMetadata/v1/workSkillConditions"
        logging.info(
            f"Fetching work skill conditions from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint)
        return WorkskillConditionListResponse.from_response(response)

    # Work Skill Groups API
    async def get_workskill_groups(self) -> WorkSkillGroupListResponse:
        """Get work skill groups list.

        Returns:
            WorkSkillGroupListResponse response model with list of work skill groups
        """
        endpoint = "/rest/ofscMetadata/v1/workSkillGroups"
        logging.info(
            f"Fetching work skill groups from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint)
        return WorkSkillGroupListResponse.from_response(response)

    async def get_workskill_group(self, label: str) -> WorkSkillGroup:
        """Get single work skill group by label.

        Args:
            label: Work skill group label identifier

        Returns:
            WorkSkillGroup response model

        Raises:
            OFSValidationException: If label is invalid
        """
        self._validate_params(LabelParam, label=label)

        endpoint = f"/rest/ofscMetadata/v1/workSkillGroups/{label}"
        response: "Response" = await self.client.get(endpoint)
        return WorkSkillGroup.from_response(response)

    # Capacity Areas API
    async def get_capacity_areas(
        self,
        expandParent: bool = False,
        fields: List[str] = ["label"],
        activeOnly: bool = False,
        areasOnly: bool = False,
    ) -> CapacityAreaListResponse:
        """Get capacity areas list.

        Args:
            expandParent: Expand parent area information (default: False)
            fields: Fields to include in response (default: ["label"])
            activeOnly: Return only active areas (default: False)
            areasOnly: Return only area type entries (default: False)

        Returns:
            CapacityAreaListResponse response model with list of capacity areas

        Raises:
            OFSValidationException: If parameters are invalid
        """
        validated_params = self._validate_params(
            CapacityAreasParams,
            expandParent=expandParent,
            fields=fields,
            activeOnly=activeOnly,
            areasOnly=areasOnly,
        )

        # Build query parameters according to v2.x implementation
        params = {
            "expand": "parent" if validated_params["expandParent"] else None,
            "fields": ",".join(validated_params["fields"])
            if validated_params["fields"]
            else None,
            "status": "active" if validated_params["activeOnly"] else None,
            "type": "area" if validated_params["areasOnly"] else None,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        endpoint = "/rest/ofscMetadata/v1/capacityAreas"
        logging.info(
            f"Fetching capacity areas from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return CapacityAreaListResponse.from_response(response)

    async def get_capacity_area(self, label: str) -> CapacityArea:
        """Get single capacity area by label.

        Args:
            label: Capacity area label identifier

        Returns:
            CapacityArea response model

        Raises:
            OFSValidationException: If label is invalid
        """
        self._validate_params(LabelParam, label=label)

        encoded_label = urllib.parse.quote_plus(label)
        endpoint = f"/rest/ofscMetadata/v1/capacityAreas/{encoded_label}"
        response: "Response" = await self.client.get(endpoint)
        return CapacityArea.from_response(response)

    # Capacity Categories API
    async def get_capacity_categories(
        self, offset: int = 0, limit: int = 100
    ) -> CapacityCategoryListResponse:
        """Get capacity categories list.

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            CapacityCategoryListResponse response model with list of capacity categories

        Raises:
            OFSValidationException: If parameters are invalid
        """
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        endpoint = "/rest/ofscMetadata/v1/capacityCategories"
        logging.info(
            f"Fetching capacity categories from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return CapacityCategoryListResponse.from_response(response)

    async def get_capacity_category(self, label: str) -> CapacityCategory:
        """Get single capacity category by label.

        Args:
            label: Capacity category label identifier

        Returns:
            CapacityCategory response model

        Raises:
            OFSValidationException: If label is invalid
        """
        self._validate_params(LabelParam, label=label)

        encoded_label = urllib.parse.quote_plus(label)
        endpoint = f"/rest/ofscMetadata/v1/capacityCategories/{encoded_label}"
        response: "Response" = await self.client.get(endpoint)
        return CapacityCategory.from_response(response)

    # Inventory Types API
    async def get_inventory_types(self) -> InventoryTypeListResponse:
        """Get inventory types list.

        Returns:
            InventoryTypeListResponse response model with list of inventory types
        """
        endpoint = "/rest/ofscMetadata/v1/inventoryTypes"
        logging.info(
            f"Fetching inventory types from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint)
        return InventoryTypeListResponse.from_response(response)

    async def get_inventory_type(self, label: str) -> InventoryType:
        """Get single inventory type by label.

        Args:
            label: Inventory type label identifier

        Returns:
            InventoryType response model

        Raises:
            OFSValidationException: If label is invalid
        """
        self._validate_params(LabelParam, label=label)

        encoded_label = urllib.parse.quote_plus(label)
        endpoint = f"/rest/ofscMetadata/v1/inventoryTypes/{encoded_label}"
        response: "Response" = await self.client.get(endpoint)
        return InventoryType.from_response(response)

    # Applications API
    async def get_applications(self) -> ApplicationListResponse:
        """Get applications list.

        Returns:
            ApplicationListResponse response model with list of applications
        """
        endpoint = "/rest/ofscMetadata/v1/applications"
        logging.info(
            f"Fetching applications from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint)
        return ApplicationListResponse.from_response(response)

    async def get_application(self, label: str) -> Application:
        """Get single application by label.

        Args:
            label: Application label identifier

        Returns:
            Application response model

        Raises:
            OFSValidationException: If label is invalid
        """
        self._validate_params(LabelParam, label=label)

        endpoint = f"/rest/ofscMetadata/v1/applications/{label}"
        response: "Response" = await self.client.get(endpoint)
        return Application.from_response(response)

    async def get_application_api_accesses(self, label: str):
        """Get application API accesses by application label.

        Args:
            label: Application label identifier

        Returns:
            API access response model

        Raises:
            OFSValidationException: If label is invalid
        """
        self._validate_params(LabelParam, label=label)

        endpoint = f"/rest/ofscMetadata/v1/applications/{label}/apiAccess"
        response: "Response" = await self.client.get(endpoint)
        # Note: Using generic response parsing as specific model not defined in original
        return response.json()

    async def get_application_api_access(self, label: str, accessId: str):
        """Get specific application API access by application label and access ID.

        Args:
            label: Application label identifier
            accessId: API access ID

        Returns:
            API access response model

        Raises:
            OFSValidationException: If label is invalid
        """
        self._validate_params(LabelParam, label=label)

        endpoint = f"/rest/ofscMetadata/v1/applications/{label}/apiAccess/{accessId}"
        response: "Response" = await self.client.get(endpoint)
        # Note: Using generic response parsing as specific model not defined in original
        return response.json()

    # Organizations API
    async def get_organizations(self) -> OrganizationListResponse:
        """Get organizations list.

        Returns:
            OrganizationListResponse response model with list of organizations
        """
        endpoint = "/rest/ofscMetadata/v1/organizations"
        logging.info(
            f"Fetching organizations from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint)
        return OrganizationListResponse.from_response(response)

    async def get_organization(self, label: str) -> Organization:
        """Get single organization by label.

        Args:
            label: Organization label identifier

        Returns:
            Organization response model

        Raises:
            OFSValidationException: If label is invalid
        """
        self._validate_params(LabelParam, label=label)

        endpoint = f"/rest/ofscMetadata/v1/organizations/{label}"
        response: "Response" = await self.client.get(endpoint)
        return Organization.from_response(response)

    # Time Slots API
    async def get_timeslots(
        self, offset: int = 0, limit: int = 100
    ) -> TimeSlotListResponse:
        """Get time slots list.

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            TimeSlotListResponse response model with list of time slots

        Raises:
            OFSValidationException: If parameters are invalid
        """
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        endpoint = "/rest/ofscMetadata/v1/timeSlots"
        logging.info(
            f"Fetching time slots from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return TimeSlotListResponse.from_response(response)

    # Capacity Area Sub-Resource APIs (Endpoints 16-21)
    async def get_capacity_area_categories(
        self, area_label: str, offset: int = 0, limit: int = 100
    ) -> CapacityAreaCategoryListResponse:
        """Get capacity categories for a specific capacity area.

        Args:
            area_label: Capacity area label identifier
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            CapacityAreaCategoryListResponse response model with list of capacity categories

        Raises:
            OFSValidationException: If parameters are invalid
        """
        self._validate_params(LabelParam, label=area_label)
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        encoded_label = urllib.parse.quote_plus(area_label)
        endpoint = (
            f"/rest/ofscMetadata/v1/capacityAreas/{encoded_label}/capacityCategories"
        )
        logging.info(
            f"Fetching capacity area categories from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return CapacityAreaCategoryListResponse.from_response(response)

    async def get_capacity_area_workzones(
        self, area_label: str, offset: int = 0, limit: int = 100
    ) -> CapacityAreaWorkzoneListResponse:
        """Get work zones for a specific capacity area (v2 endpoint with detailed info).

        Args:
            area_label: Capacity area label identifier
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            CapacityAreaWorkzoneListResponse response model with list of work zones

        Raises:
            OFSValidationException: If parameters are invalid
        """
        self._validate_params(LabelParam, label=area_label)
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        encoded_label = urllib.parse.quote_plus(area_label)
        endpoint = f"/rest/ofscMetadata/v2/capacityAreas/{encoded_label}/workZones"
        logging.info(
            f"Fetching capacity area work zones (v2) from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return CapacityAreaWorkzoneListResponse.from_response(response)

    async def get_capacity_area_timeslots(
        self, area_label: str, offset: int = 0, limit: int = 100
    ) -> CapacityAreaTimeSlotListResponse:
        """Get time slots for a specific capacity area.

        Args:
            area_label: Capacity area label identifier
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            CapacityAreaTimeSlotListResponse response model with list of time slots

        Raises:
            OFSValidationException: If parameters are invalid
        """
        self._validate_params(LabelParam, label=area_label)
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        encoded_label = urllib.parse.quote_plus(area_label)
        endpoint = f"/rest/ofscMetadata/v1/capacityAreas/{encoded_label}/timeSlots"
        logging.info(
            f"Fetching capacity area time slots from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return CapacityAreaTimeSlotListResponse.from_response(response)

    async def get_capacity_area_timeintervals(
        self, area_label: str, offset: int = 0, limit: int = 100
    ) -> CapacityAreaTimeIntervalListResponse:
        """Get time intervals for a specific capacity area.

        Args:
            area_label: Capacity area label identifier
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            CapacityAreaTimeIntervalListResponse response model with list of time intervals

        Raises:
            OFSValidationException: If parameters are invalid
        """
        self._validate_params(LabelParam, label=area_label)
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        encoded_label = urllib.parse.quote_plus(area_label)
        endpoint = f"/rest/ofscMetadata/v1/capacityAreas/{encoded_label}/timeIntervals"
        logging.info(
            f"Fetching capacity area time intervals from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return CapacityAreaTimeIntervalListResponse.from_response(response)

    async def get_capacity_area_organizations(
        self, area_label: str, offset: int = 0, limit: int = 100
    ) -> CapacityAreaOrganizationListResponse:
        """Get organizations for a specific capacity area.

        Args:
            area_label: Capacity area label identifier
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            CapacityAreaOrganizationListResponse response model with list of organizations

        Raises:
            OFSValidationException: If parameters are invalid
        """
        self._validate_params(LabelParam, label=area_label)
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        encoded_label = urllib.parse.quote_plus(area_label)
        endpoint = f"/rest/ofscMetadata/v1/capacityAreas/{encoded_label}/organizations"
        logging.info(
            f"Fetching capacity area organizations from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return CapacityAreaOrganizationListResponse.from_response(response)
