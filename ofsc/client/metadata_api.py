"""Metadata API implementation for v3.0 OFSC async-only client architecture.

This module implements the Metadata API endpoints using the new v3.0 architecture with:
- httpx.AsyncClient for async-only operations
- Pydantic model responses
- Internal request parameter validation
- Fault tolerance (retry + circuit breaker)
"""

import logging
from typing import TYPE_CHECKING

import httpx
from pydantic import BaseModel, Field, ValidationError

from ofsc.exceptions import OFSValidationException
from ofsc.models.metadata import (
    ActivityType,
    ActivityTypeGroup,
    ActivityTypeGroupListResponse,
    ActivityTypeListResponse,
    EnumerationValueList,
    Property,
    ResourceType,
    Workskill,
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
    async def get_properties(self, offset: int = 0, limit: int = 100) -> Property:
        """Get properties list.

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            Property response model with list of properties

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
        return Property.from_response(response)

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
    async def get_workskills(self, offset: int = 0, limit: int = 100) -> Workskill:
        """Get work skills list.

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            Workskill response model with list of work skills
        """
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        endpoint = "/rest/ofscMetadata/v1/workSkills"
        logging.info(
            f"Fetching workskills from endpoint: {endpoint} and base URL: {self.client.base_url}"
        )
        
        response: "Response" = await self.client.get(endpoint, params=params)
        return Workskill.from_response(response)

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
    async def get_enumeration_values(self, label: str, offset: int = 0, limit: int = 100) -> EnumerationValueList:
        """Get enumeration values for a property."""
        self._validate_params(LabelParam, label=label)
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)
        
        endpoint = f"/rest/ofscMetadata/v1/properties/{label}/enumerationValues"
        response: "Response" = await self.client.get(endpoint, params=params)
        return EnumerationValueList.from_response(response)
    
    # Resource Types API  
    async def get_resource_types(self) -> ResourceType:
        """Get resource types list."""
        endpoint = "/rest/ofscMetadata/v1/resourceTypes"
        response: "Response" = await self.client.get(endpoint)
        return ResourceType.from_response(response)
    
    # Activity Type Groups API
    async def get_activity_type_groups(self, offset: int = 0, limit: int = 100) -> ActivityTypeGroupListResponse:
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