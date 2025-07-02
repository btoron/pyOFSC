"""Capacity API client for OFSC Python Wrapper v3.0.

This module provides the CapacityAPI class for interacting with OFSC Capacity API endpoints.
All methods are async and return Pydantic models.
"""

from typing import List, Optional
from urllib.parse import quote

from ..models.capacity import (
    GetCapacityResponse,
    GetQuotaResponse,
    CapacityRequest,
    GetQuotaRequest,
)


class CapacityAPI:
    """Async client for OFSC Capacity API endpoints."""

    def __init__(self, client):
        """Initialize with base OFSC client."""
        self._client = client

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
        # Create request model for validation
        request_data = CapacityRequest(
            dates=dates,
            areas=areas,
            categories=categories,
            fields=fields,
            aggregateResults=aggregateResults,
            availableTimeIntervals=availableTimeIntervals,
            calendarTimeIntervals=calendarTimeIntervals,
        )
        
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

        response = await self._client._make_request(
            method="GET",
            url="/rest/ofscCapacity/v1/capacity",
            params=params,
        )
        
        return GetCapacityResponse.model_validate(response)

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
        # Create request model for validation
        request_data = GetQuotaRequest(
            dates=dates,
            areas=areas,
            categories=categories,
            aggregateResults=aggregateResults,
            categoryLevel=categoryLevel,
            intervalLevel=intervalLevel,
            returnStatuses=returnStatuses,
            timeSlotLevel=timeSlotLevel,
        )
        
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

        response = await self._client._make_request(
            method="GET",
            url="/rest/ofscCapacity/v1/quota",
            params=params,
        )
        
        return GetQuotaResponse.model_validate(response)

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
        # Create request model for validation
        request_data = GetQuotaRequest(
            dates=dates,
            areas=areas,
            categories=categories,
            aggregateResults=aggregateResults,
            categoryLevel=categoryLevel,
            intervalLevel=intervalLevel,
            returnStatuses=returnStatuses,
            timeSlotLevel=timeSlotLevel,
        )
        
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

        response = await self._client._make_request(
            method="PATCH",
            url="/rest/ofscCapacity/v1/quota",
            params=params,
            json=request_body,
        )
        
        return GetQuotaResponse.model_validate(response)