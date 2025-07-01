"""Metadata API implementation for v3.0 OFSC async-only client architecture.

This module implements the Metadata API endpoints using the new v3.0 architecture with:
- httpx.AsyncClient for async-only operations
- Pydantic model responses
- Internal request parameter validation
- Fault tolerance (retry + circuit breaker)
"""

import logging
import urllib.parse
from typing import TYPE_CHECKING, List, Optional

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
    ApplicationApiAccess,
    ApplicationApiAccessListResponse,
    ApplicationListResponse,
    EnumerationValueList,
    Form,
    FormListResponse,
    InventoryType,
    InventoryTypeListResponse,
    LanguageListResponse,
    LinkTemplate,
    LinkTemplateListResponse,
    NonWorkingReasonListResponse,
    Organization,
    OrganizationListResponse,
    Property,
    PropertyListResponse,
    ResourceTypeListResponse,
    RoutingProfileListResponse,
    RoutingPlanListResponse,
    RoutingPlanExportResponse,
    ExportMediaType,
    Shift,
    ShiftListResponse,
    TimeSlotListResponse,
    Workskill,
    WorkskillConditionListResponse,
    WorkSkillGroup,
    WorkSkillGroupListResponse,
    WorkskillListResponse,
    Workzone,
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

    async def get_application_api_accesses(self, label: str) -> ApplicationApiAccessListResponse:
        """Get application API accesses by application label.

        Args:
            label: Application label identifier

        Returns:
            ApplicationApiAccessListResponse: Typed response with API access list

        Raises:
            OFSValidationException: If label is invalid
        """
        self._validate_params(LabelParam, label=label)

        endpoint = f"/rest/ofscMetadata/v1/applications/{label}/apiAccess"
        response: "Response" = await self.client.get(endpoint)
        return ApplicationApiAccessListResponse.from_response(response)

    async def get_application_api_access(self, label: str, api_label: str) -> ApplicationApiAccess:
        """Get specific application API access by application label and API access label.

        Args:
            label: Application label identifier
            api_label: API access label (e.g., 'metadataAPI', 'coreAPI')

        Returns:
            ApplicationApiAccess: Individual API access configuration

        Raises:
            OFSValidationException: If parameters are invalid
        """
        self._validate_params(LabelParam, label=label)
        # URL encode the api_label to handle special characters
        encoded_api_label = urllib.parse.quote_plus(api_label)

        endpoint = f"/rest/ofscMetadata/v1/applications/{label}/apiAccess/{encoded_api_label}"
        response: "Response" = await self.client.get(endpoint)
        return ApplicationApiAccess.from_response(response)

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

    # Languages API
    async def get_languages(
        self, offset: int = 0, limit: int = 100
    ) -> LanguageListResponse:
        """Get languages list.

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            LanguageListResponse response model with list of languages

        Raises:
            OFSValidationException: If parameters are invalid
        """
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        endpoint = "/rest/ofscMetadata/v1/languages"
        logging.info(
            f"Fetching languages from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return LanguageListResponse.from_response(response)

    # Non-Working Reasons API  
    async def get_non_working_reasons(
        self, offset: int = 0, limit: int = 100
    ) -> NonWorkingReasonListResponse:
        """Get non-working reasons list.

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            NonWorkingReasonListResponse response model with list of non-working reasons

        Raises:
            OFSValidationException: If parameters are invalid
        """
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        endpoint = "/rest/ofscMetadata/v1/nonWorkingReasons"
        logging.info(
            f"Fetching non-working reasons from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return NonWorkingReasonListResponse.from_response(response)

    # Shifts API
    async def get_shifts(
        self, offset: int = 0, limit: int = 100
    ) -> ShiftListResponse:
        """Get shifts list.

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            ShiftListResponse response model with list of shifts

        Raises:
            OFSValidationException: If parameters are invalid
        """
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        endpoint = "/rest/ofscMetadata/v1/shifts"
        logging.info(
            f"Fetching shifts from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return ShiftListResponse.from_response(response)

    async def get_shift(self, label: str) -> Shift:
        """Get individual shift by label.

        Args:
            label: Shift label identifier

        Returns:
            Shift response model with shift details

        Raises:
            OFSValidationException: If parameters are invalid
        """
        encoded_label = urllib.parse.quote_plus(label)
        endpoint = f"/rest/ofscMetadata/v1/shifts/{encoded_label}"
        logging.info(
            f"Fetching shift from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint)
        return Shift.from_response(response)

    # Forms API
    async def get_forms(self, offset: int = 0, limit: int = 100) -> FormListResponse:
        """Get forms list.

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            FormListResponse response model with list of forms

        Raises:
            OFSValidationException: If parameters are invalid
        """
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        endpoint = "/rest/ofscMetadata/v1/forms"
        logging.info(
            f"Fetching forms from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return FormListResponse.from_response(response)

    async def get_form(self, label: str) -> Form:
        """Get individual form by label.

        Args:
            label: Form label identifier

        Returns:
            Form response model with form details

        Raises:
            OFSValidationException: If parameters are invalid
        """
        encoded_label = urllib.parse.quote_plus(label)
        endpoint = f"/rest/ofscMetadata/v1/forms/{encoded_label}"
        logging.info(
            f"Fetching form from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint)
        return Form.from_response(response)

    # Link Templates API
    async def get_link_templates(
        self, offset: int = 0, limit: int = 100
    ) -> LinkTemplateListResponse:
        """Get link templates list.

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            LinkTemplateListResponse response model with list of link templates

        Raises:
            OFSValidationException: If parameters are invalid
        """
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        endpoint = "/rest/ofscMetadata/v1/linkTemplates"
        logging.info(
            f"Fetching link templates from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return LinkTemplateListResponse.from_response(response)

    async def get_link_template(self, label: str) -> LinkTemplate:
        """Get individual link template by label.

        Args:
            label: Link template label identifier

        Returns:
            LinkTemplate response model with link template details

        Raises:
            OFSValidationException: If parameters are invalid
        """
        encoded_label = urllib.parse.quote_plus(label)
        endpoint = f"/rest/ofscMetadata/v1/linkTemplates/{encoded_label}"
        logging.info(
            f"Fetching link template from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint)
        return LinkTemplate.from_response(response)

    # Routing Profiles API
    async def get_routing_profiles(
        self, offset: int = 0, limit: int = 100
    ) -> RoutingProfileListResponse:
        """Get routing profiles list.

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            RoutingProfileListResponse response model with list of routing profiles

        Raises:
            OFSValidationException: If parameters are invalid
        """
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        endpoint = "/rest/ofscMetadata/v1/routingProfiles"
        logging.info(
            f"Fetching routing profiles from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return RoutingProfileListResponse.from_response(response)

    async def get_routing_profile_plans(
        self, profile_label: str, offset: int = 0, limit: int = 100
    ) -> RoutingPlanListResponse:
        """Get routing plans for a specific routing profile.

        Args:
            profile_label: Routing profile label identifier
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            RoutingPlanListResponse response model with list of routing plans

        Raises:
            OFSValidationException: If parameters are invalid
        """
        self._validate_params(LabelParam, label=profile_label)
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        encoded_label = urllib.parse.quote_plus(profile_label)
        endpoint = f"/rest/ofscMetadata/v1/routingProfiles/{encoded_label}/plans"
        logging.info(
            f"Fetching routing profile plans from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, params=params)
        return RoutingPlanListResponse.from_response(response)

    async def get_routing_profile_plan_export(
        self, profile_label: str, plan_label: str, media_type: Optional[str] = ExportMediaType.OCTET_STREAM.value
    ) -> RoutingPlanExportResponse:
        """Export routing plan configuration for a specific routing profile and plan.

        Args:
            profile_label: Routing profile label identifier
            plan_label: Routing plan label identifier
            media_type: Media type for export format (default: application/octet-stream)
                       Supported values: application/json, text/csv, application/xml, application/octet-stream

        Returns:
            RoutingPlanExportResponse response model with export download information

        Raises:
            OFSValidationException: If parameters are invalid
        """
        self._validate_params(LabelParam, label=profile_label)
        self._validate_params(LabelParam, label=plan_label)

        # Validate media type parameter
        if media_type is not None and media_type not in [mt.value for mt in ExportMediaType]:
            raise OFSValidationException(f"Invalid media type: {media_type}. Supported types: {[mt.value for mt in ExportMediaType]}")

        # Set Accept header with requested media type (if specified)
        headers = {}
        if media_type is not None:
            headers["Accept"] = media_type

        encoded_profile_label = urllib.parse.quote_plus(profile_label)
        encoded_plan_label = urllib.parse.quote_plus(plan_label)
        endpoint = f"/rest/ofscMetadata/v1/routingProfiles/{encoded_profile_label}/plans/{encoded_plan_label}/custom-actions/export"
        logging.info(
            f"Fetching routing profile plan export from endpoint: {endpoint}"
            + (f" with Accept: {media_type}" if media_type else " (no Accept header)")
            + f" and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint, headers=headers if headers else None)
        return RoutingPlanExportResponse.from_response(response)

    # Workzones API (individual endpoint)
    async def get_workzone(self, label: str) -> Workzone:
        """Get individual workzone by label.

        Args:
            label: Workzone label identifier

        Returns:
            Workzone response model with workzone details

        Raises:
            OFSValidationException: If parameters are invalid
        """
        encoded_label = urllib.parse.quote_plus(label)
        endpoint = f"/rest/ofscMetadata/v1/workZones/{encoded_label}"
        logging.info(
            f"Fetching workzone from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )

        response: "Response" = await self.client.get(endpoint)
        return Workzone.from_response(response)
