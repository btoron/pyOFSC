"""Metadata API implementation for v3.0 OFSC client architecture.

This module implements the Metadata API endpoints using the new v3.0 architecture with:
- httpx-based HTTP client
- Pydantic model responses
- Internal request parameter validation
- Fault tolerance (retry + circuit breaker)
- Both sync and async support
"""

import logging
from typing import Union
from urllib.parse import urljoin  # TODO: Avoid direct import, use client module instead

import httpx  # TODO: Avoid direct import, use client module instead
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
    """Metadata API client for both sync and async operations."""

    def __init__(
        self,
        client: Union[httpx.Client, httpx.AsyncClient],
        base_url: str,
        auth_headers: dict,
    ):
        """Initialize the Metadata API client.

        Args:
            client: httpx Client or AsyncClient instance
            base_url: Base URL for the OFSC instance
            auth_headers: Authentication headers
        """
        self._client = client
        self._base_url = base_url
        self._auth_headers = auth_headers
        self._is_async = isinstance(client, httpx.AsyncClient)

    def _build_url(self, endpoint: str) -> str:
        """Build full URL for metadata API endpoint."""
        return urljoin(self._base_url, f"/rest/ofscMetadata/v1/{endpoint}")

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
    async def aget_properties(self, offset: int = 0, limit: int = 100) -> Property:
        """Get properties list (async).

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            Property response model with list of properties

        Raises:
            OFSValidationException: If parameters are invalid
        """
        if not self._is_async:
            raise RuntimeError("This method can only be called on async clients")

        # Validate parameters
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        url = self._build_url("properties")
        response = await self._client.get(
            url, headers=self._auth_headers, params=params
        )

        # For now, return a basic Property model - will be enhanced in next step
        return Property.from_response(response)

    def get_properties(self, offset: int = 0, limit: int = 100) -> Property:
        """Get properties list (sync).

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            Property response model with list of properties

        Raises:
            OFSValidationException: If parameters are invalid
        """
        if self._is_async:
            raise RuntimeError("This method can only be called on sync clients")

        # Validate parameters
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        url = self._build_url("properties")
        response = self._client.get(url, headers=self._auth_headers, params=params)

        # For now, return a basic Property model - will be enhanced in next step
        return Property.from_response(response)

    async def aget_property(self, label: str) -> Property:
        """Get single property by label (async).

        Args:
            label: Property label identifier

        Returns:
            Property response model

        Raises:
            OFSValidationException: If label is invalid
        """
        if not self._is_async:
            raise RuntimeError("This method can only be called on async clients")

        # Validate parameters
        self._validate_params(LabelParam, label=label)

        url = self._build_url(f"properties/{label}")
        response = await self._client.get(url, headers=self._auth_headers)

        return Property.from_response(response)

    def get_property(self, label: str) -> Property:
        """Get single property by label (sync).

        Args:
            label: Property label identifier

        Returns:
            Property response model

        Raises:
            OFSValidationException: If label is invalid
        """
        if self._is_async:
            raise RuntimeError("This method can only be called on sync clients")

        # Validate parameters
        self._validate_params(LabelParam, label=label)

        url = self._build_url(f"properties/{label}")
        response = self._client.get(url, headers=self._auth_headers)

        return Property.from_response(response)

    # Work Skills API
    async def aget_workskills(self, offset: int = 0, limit: int = 100) -> Workskill:
        """Get work skills list (async).

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            Workskill response model with list of work skills
        """
        if not self._is_async:
            raise RuntimeError("This method can only be called on async clients")

        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        url = self._build_url("workSkills")
        response = await self._client.get(
            url, headers=self._auth_headers, params=params
        )

        return Workskill.from_response(response)

    def get_workskills(self, offset: int = 0, limit: int = 100) -> Workskill:
        """Get work skills list (sync).

        Args:
            offset: Starting record offset (default: 0)
            limit: Maximum records to return (default: 100, max: 1000)

        Returns:
            Workskill response model with list of work skills
        """
        if self._is_async:
            raise RuntimeError("This method can only be called on sync clients")

        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        url = self._build_url("workSkills")
        response = self._client.get(url, headers=self._auth_headers, params=params)

        return Workskill.from_response(response)

    async def aget_workskill(self, label: str) -> Workskill:
        """Get single work skill by label (async)."""
        if not self._is_async:
            raise RuntimeError("This method can only be called on async clients")

        self._validate_params(LabelParam, label=label)

        url = self._build_url(f"workSkills/{label}")
        response = await self._client.get(url, headers=self._auth_headers)

        return Workskill.from_response(response)

    def get_workskill(self, label: str) -> Workskill:
        """Get single work skill by label (sync)."""
        if self._is_async:
            raise RuntimeError("This method can only be called on sync clients")

        self._validate_params(LabelParam, label=label)

        url = self._build_url(f"workSkills/{label}")
        response = self._client.get(url, headers=self._auth_headers)

        return Workskill.from_response(response)

    # Activity Types API
    async def aget_activity_types(
        self, offset: int = 0, limit: int = 100
    ) -> ActivityTypeListResponse:
        """Get activity types list (async)."""
        if not self._is_async:
            raise RuntimeError("This method can only be called on async clients")

        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        url = self._build_url("activityTypes")
        response = await self._client.get(
            url, headers=self._auth_headers, params=params
        )

        return ActivityTypeListResponse.from_response(response)

    def get_activity_types(
        self, offset: int = 0, limit: int = 100
    ) -> ActivityTypeListResponse:
        """Get activity types list (sync)."""
        if self._is_async:
            raise RuntimeError("This method can only be called on sync clients")

        params = self._validate_params(PaginationParams, offset=offset, limit=limit)

        url = self._build_url("activityTypes")
        response = self._client.get(url, headers=self._auth_headers, params=params)

        return ActivityTypeListResponse.from_response(response)

    async def aget_activity_type(self, label: str) -> ActivityType:
        """Get single activity type by label (async)."""
        if not self._is_async:
            raise RuntimeError("This method can only be called on async clients")

        self._validate_params(LabelParam, label=label)

        url = self._build_url(f"activityTypes/{label}")
        response = await self._client.get(url, headers=self._auth_headers)

        return ActivityType.from_response(response)

    def get_activity_type(self, label: str) -> ActivityType:
        """Get single activity type by label (sync)."""
        if self._is_async:
            raise RuntimeError("This method can only be called on sync clients")

        self._validate_params(LabelParam, label=label)

        url = self._build_url(f"activityTypes/{label}")
        response = self._client.get(url, headers=self._auth_headers)

        return ActivityType.from_response(response)
    
    # Additional Metadata API endpoints
    async def aget_enumeration_values(self, label: str, offset: int = 0, limit: int = 100) -> EnumerationValueList:
        """Get enumeration values for a property (async)."""
        if not self._is_async:
            raise RuntimeError("This method can only be called on async clients")
            
        self._validate_params(LabelParam, label=label)
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)
        
        url = self._build_url(f"properties/{label}/enumerationValues")
        response = await self._client.get(url, headers=self._auth_headers, params=params)
        
        return EnumerationValueList.from_response(response)
    
    def get_enumeration_values(self, label: str, offset: int = 0, limit: int = 100) -> EnumerationValueList:
        """Get enumeration values for a property (sync)."""
        if self._is_async:
            raise RuntimeError("This method can only be called on sync clients")
            
        self._validate_params(LabelParam, label=label)
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)
        
        url = self._build_url(f"properties/{label}/enumerationValues")
        response = self._client.get(url, headers=self._auth_headers, params=params)
        
        return EnumerationValueList.from_response(response)
    
    # Resource Types API  
    async def aget_resource_types(self) -> ResourceType:
        """Get resource types list (async)."""
        if not self._is_async:
            raise RuntimeError("This method can only be called on async clients")
            
        url = self._build_url("resourceTypes")
        response = await self._client.get(url, headers=self._auth_headers)
        
        return ResourceType.from_response(response)
    
    def get_resource_types(self) -> ResourceType:
        """Get resource types list (sync)."""
        if self._is_async:
            raise RuntimeError("This method can only be called on sync clients")
            
        url = self._build_url("resourceTypes")
        response = self._client.get(url, headers=self._auth_headers)
        
        return ResourceType.from_response(response)
    
    # Activity Type Groups API
    async def aget_activity_type_groups(self, offset: int = 0, limit: int = 100) -> ActivityTypeGroupListResponse:
        """Get activity type groups list (async)."""
        if not self._is_async:
            raise RuntimeError("This method can only be called on async clients")
            
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)
        
        url = self._build_url("activityTypeGroups")
        response = await self._client.get(url, headers=self._auth_headers, params=params)
        
        return ActivityTypeGroupListResponse.from_response(response)
    
    def get_activity_type_groups(self, offset: int = 0, limit: int = 100) -> ActivityTypeGroupListResponse:
        """Get activity type groups list (sync)."""
        if self._is_async:
            raise RuntimeError("This method can only be called on sync clients")
            
        params = self._validate_params(PaginationParams, offset=offset, limit=limit)
        
        url = self._build_url("activityTypeGroups")
        response = self._client.get(url, headers=self._auth_headers, params=params)
        
        return ActivityTypeGroupListResponse.from_response(response)
    
    async def aget_activity_type_group(self, label: str) -> ActivityTypeGroup:
        """Get single activity type group by label (async)."""
        if not self._is_async:
            raise RuntimeError("This method can only be called on async clients")
            
        self._validate_params(LabelParam, label=label)
        
        url = self._build_url(f"activityTypeGroups/{label}")
        response = await self._client.get(url, headers=self._auth_headers)
        
        return ActivityTypeGroup.from_response(response)
    
    def get_activity_type_group(self, label: str) -> ActivityTypeGroup:
        """Get single activity type group by label (sync)."""
        if self._is_async:
            raise RuntimeError("This method can only be called on sync clients")
            
        self._validate_params(LabelParam, label=label)
        
        url = self._build_url(f"activityTypeGroups/{label}")
        response = self._client.get(url, headers=self._auth_headers)
        
        return ActivityTypeGroup.from_response(response)
