"""Capacity API client for OFSC Python Wrapper v3.0.

This module provides the CapacityAPI class for interacting with OFSC Capacity API endpoints.
All methods are async and return Pydantic models.
"""

from typing import List, Optional
from urllib.parse import quote

import httpx
from pydantic import BaseModel, Field, ValidationError

from ofsc.exceptions import OFSValidationException
from ..models.capacity import (
    GetCapacityResponse,
    GetQuotaResponse,
    CapacityRequest,
    GetQuotaRequest,
)


# Request validation models (internal use only)
class GetCapacityParams(BaseModel):
    """Internal validation for get capacity parameters."""
    
    dates: List[str] = Field(description="List of dates in YYYY-MM-DD format")
    areas: Optional[List[str]] = Field(None, description="List of capacity area labels")
    categories: Optional[List[str]] = Field(None, description="List of capacity category labels")
    fields: Optional[List[str]] = Field(None, description="List of fields to include")
    aggregateResults: bool = Field(False, description="Whether to aggregate results")
    availableTimeIntervals: str = Field("all", description="Available time intervals filter")
    calendarTimeIntervals: str = Field("all", description="Calendar time intervals filter")


class GetQuotaParams(BaseModel):
    """Internal validation for get quota parameters."""
    
    dates: List[str] = Field(description="List of dates in YYYY-MM-DD format")
    areas: Optional[List[str]] = Field(None, description="List of capacity area labels")
    categories: Optional[List[str]] = Field(None, description="List of capacity category labels")
    aggregateResults: Optional[bool] = Field(None, description="Whether to aggregate results")
    categoryLevel: Optional[bool] = Field(None, description="Include category-level quota")
    intervalLevel: Optional[bool] = Field(None, description="Include interval-level quota")
    returnStatuses: Optional[bool] = Field(None, description="Include quota status information")
    timeSlotLevel: Optional[bool] = Field(None, description="Include time slot-level quota")


class CapacityAPI:
    """Async client for OFSC Capacity API endpoints."""

    def __init__(self, client: httpx.AsyncClient):
        """Initialize with httpx AsyncClient instance.
        
        Args:
            client: httpx AsyncClient instance with base_url and auth headers configured
        """
        self.client = client

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
            model = model_class(**kwargs)
            # Convert to dict, excluding None values
            return model.model_dump(exclude_none=True)
        except ValidationError as e:
            raise OFSValidationException(
                message=f"Invalid parameters for {model_class.__name__}",
                errors=e.errors()
            )

    async def get_capacity(
        self,
        dates: List[str],
        areas: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        aggregateResults: bool = False,
        availableTimeIntervals: str = "all",
        calendarTimeIntervals: str = "all",
    ) -> GetCapacityResponse:
        """Get capacity information for specified dates and areas.
        
        Args:
            dates: List of dates in YYYY-MM-DD format (required)
            areas: List of capacity area labels to filter by
            categories: List of capacity category labels to filter by
            fields: List of fields to include in response
            aggregateResults: Whether to aggregate results across areas
            availableTimeIntervals: Available time intervals filter ("all", "none", or specific)
            calendarTimeIntervals: Calendar time intervals filter ("all", "none", or specific)
            
        Returns:
            GetCapacityResponse: Capacity data for the specified parameters
        """
        # Validate parameters
        validated_params = self._validate_params(
            GetCapacityParams,
            dates=dates,
            areas=areas,
            categories=categories,
            fields=fields,
            aggregateResults=aggregateResults,
            availableTimeIntervals=availableTimeIntervals,
            calendarTimeIntervals=calendarTimeIntervals,
        )
        
        # Create request model for CSV formatting
        request_data = CapacityRequest(**validated_params)
        
        # Build query parameters
        params = {}
        
        # Required parameters
        params["dates"] = request_data.dates.value if request_data.dates else ""
        
        # Optional parameters
        if request_data.areas:
            params["areas"] = request_data.areas.value
        if request_data.categories:
            params["categories"] = request_data.categories.value
        if request_data.fields:
            params["fields"] = request_data.fields.value
        if request_data.aggregateResults is not None:
            params["aggregateResults"] = str(request_data.aggregateResults).lower()
        if request_data.availableTimeIntervals:
            params["availableTimeIntervals"] = request_data.availableTimeIntervals
        if request_data.calendarTimeIntervals:
            params["calendarTimeIntervals"] = request_data.calendarTimeIntervals

        response = await self.client.request(
            method="GET",
            url="/rest/ofscCapacity/v1/capacity",
            params=params,
        )
        
        return GetCapacityResponse.from_response(response)

    async def get_quota(
        self,
        dates: List[str],
        areas: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        aggregateResults: Optional[bool] = None,
        categoryLevel: Optional[bool] = None,
        intervalLevel: Optional[bool] = None,
        returnStatuses: Optional[bool] = None,
        timeSlotLevel: Optional[bool] = None,
    ) -> GetQuotaResponse:
        """Get quota information for specified dates and areas.
        
        Args:
            dates: List of dates in YYYY-MM-DD format (required)
            areas: List of capacity area labels to filter by
            categories: List of capacity category labels to filter by
            aggregateResults: Whether to aggregate results across areas
            categoryLevel: Include category-level quota information
            intervalLevel: Include interval-level quota information
            returnStatuses: Include quota status information
            timeSlotLevel: Include time slot-level quota information
            
        Returns:
            GetQuotaResponse: Quota data for the specified parameters
        """
        # Validate parameters
        validated_params = self._validate_params(
            GetQuotaParams,
            dates=dates,
            areas=areas,
            categories=categories,
            aggregateResults=aggregateResults,
            categoryLevel=categoryLevel,
            intervalLevel=intervalLevel,
            returnStatuses=returnStatuses,
            timeSlotLevel=timeSlotLevel,
        )
        
        # Create request model for CSV formatting
        request_data = GetQuotaRequest(**validated_params)
        
        # Build query parameters
        params = {}
        
        # Required parameters
        params["dates"] = request_data.dates.value if request_data.dates else ""
        
        # Optional parameters
        if request_data.areas:
            params["areas"] = request_data.areas.value
        if request_data.categories:
            params["categories"] = request_data.categories.value
        if request_data.aggregateResults is not None:
            params["aggregateResults"] = str(request_data.aggregateResults).lower()
        if request_data.categoryLevel is not None:
            params["categoryLevel"] = str(request_data.categoryLevel).lower()
        if request_data.intervalLevel is not None:
            params["intervalLevel"] = str(request_data.intervalLevel).lower()
        if request_data.returnStatuses is not None:
            params["returnStatuses"] = str(request_data.returnStatuses).lower()
        if request_data.timeSlotLevel is not None:
            params["timeSlotLevel"] = str(request_data.timeSlotLevel).lower()

        response = await self.client.request(
            method="GET",
            url="/rest/ofscCapacity/v1/quota",
            params=params,
        )
        
        return GetQuotaResponse.from_response(response)

    async def patch_quota(
        self,
        dates: List[str],
        areas: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        aggregateResults: Optional[bool] = None,
        categoryLevel: Optional[bool] = None,
        intervalLevel: Optional[bool] = None,
        returnStatuses: Optional[bool] = None,
        timeSlotLevel: Optional[bool] = None,
        # TODO: Add request body parameters for quota modifications
    ) -> GetQuotaResponse:
        """Update quota information for specified dates and areas.
        
        Args:
            dates: List of dates in YYYY-MM-DD format (required)
            areas: List of capacity area labels to filter by
            categories: List of capacity category labels to filter by
            aggregateResults: Whether to aggregate results across areas
            categoryLevel: Include category-level quota information
            intervalLevel: Include interval-level quota information
            returnStatuses: Include quota status information
            timeSlotLevel: Include time slot-level quota information
            
        Returns:
            GetQuotaResponse: Updated quota data
            
        Note:
            This method needs the request body implementation for quota modifications.
            Currently implemented as a placeholder for the API structure.
        """
        # Validate parameters
        validated_params = self._validate_params(
            GetQuotaParams,
            dates=dates,
            areas=areas,
            categories=categories,
            aggregateResults=aggregateResults,
            categoryLevel=categoryLevel,
            intervalLevel=intervalLevel,
            returnStatuses=returnStatuses,
            timeSlotLevel=timeSlotLevel,
        )
        
        # Create request model for CSV formatting
        request_data = GetQuotaRequest(**validated_params)
        
        # Build query parameters
        params = {}
        
        # Required parameters
        params["dates"] = request_data.dates.value if request_data.dates else ""
        
        # Optional parameters
        if request_data.areas:
            params["areas"] = request_data.areas.value
        if request_data.categories:
            params["categories"] = request_data.categories.value
        if request_data.aggregateResults is not None:
            params["aggregateResults"] = str(request_data.aggregateResults).lower()
        if request_data.categoryLevel is not None:
            params["categoryLevel"] = str(request_data.categoryLevel).lower()
        if request_data.intervalLevel is not None:
            params["intervalLevel"] = str(request_data.intervalLevel).lower()
        if request_data.returnStatuses is not None:
            params["returnStatuses"] = str(request_data.returnStatuses).lower()
        if request_data.timeSlotLevel is not None:
            params["timeSlotLevel"] = str(request_data.timeSlotLevel).lower()

        # TODO: Implement request body for quota modifications
        request_body = {}

        response = await self.client.request(
            method="PATCH",
            url="/rest/ofscCapacity/v1/quota",
            params=params,
            json=request_body,
        )
        
        return GetQuotaResponse.from_response(response)