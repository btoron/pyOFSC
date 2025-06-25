from typing import Optional, Union, get_args, get_origin
from urllib.parse import urljoin

import requests
from pydantic import BaseModel

from ofsc.models import CsvList, OFSApi

from .common import OBJ_RESPONSE, wrap_return
from .models import (
    CapacityRequest,
    GetCapacityResponse,
    GetQuotaRequest,
    GetQuotaResponse,
)


def _convert_model_to_api_params(model: BaseModel) -> dict:
    """
    Convert a Pydantic BaseModel instance to API-compatible parameters dictionary.
    
    This internal function uses inspection to automatically detect and convert:
    - CsvList fields: Converts serialized CsvList objects (dict with 'value' key) to string values
    - Boolean fields: Converts boolean values to lowercase strings for API compatibility
    
    :param model: Pydantic BaseModel instance to convert
    :return: Dictionary with API-compatible parameter values
    """
    # Start with model dump, excluding None values
    params = model.model_dump(exclude_none=True)
    
    # Use inspection to get field type annotations
    model_fields = model.model_fields
    
    # Detect CsvList fields and convert them
    for field_name, field_info in model_fields.items():
        if field_name in params:
            # Check if field type is CsvList or Optional[CsvList]
            field_type = field_info.annotation
            
            # Handle Optional[CsvList] by checking Union args
            actual_type = field_type
            if get_origin(field_type) is Union:
                # For Optional[Type], Union is (Type, NoneType)
                union_args = get_args(field_type)
                non_none_types = [arg for arg in union_args if arg is not type(None)]
                if non_none_types:
                    actual_type = non_none_types[0]
            
            # Convert CsvList fields
            if actual_type is CsvList:
                field_value = params[field_name]
                if isinstance(field_value, dict) and 'value' in field_value:
                    params[field_name] = field_value['value']
            
            # Convert boolean fields to lowercase strings
            elif actual_type is bool or (get_origin(actual_type) is Union and bool in get_args(actual_type)):
                field_value = params[field_name]
                if isinstance(field_value, bool):
                    params[field_name] = str(field_value).lower()
    
    return params


class OFSCapacity(OFSApi):
    # OFSC Function Library

    @wrap_return(response_type=OBJ_RESPONSE, model=GetCapacityResponse)
    def getAvailableCapacity(self, 
                             dates: Union[list[str], CsvList, str],
                             areas: Optional[Union[list[str], CsvList, str]] = None,
                             categories: Optional[Union[list[str], CsvList, str]] = None,
                             aggregateResults: Optional[bool] = None,
                             availableTimeIntervals: str = "all",
                             calendarTimeIntervals: str = "all",
                             fields: Optional[Union[list[str], CsvList, str]] = None):
        """
        Get available capacity for a given resource or group of resources.

        This method retrieves capacity information including calendar time and available time
        for specified capacity areas and date ranges. The response includes metrics by area
        and optionally by category.

        :param dates: Required. List of dates in YYYY-MM-DD format, CsvList, or CSV string
        :param areas: Required. List of capacity area labels, CsvList, or CSV string
        :param categories: Optional. List of capacity categories, CsvList, or CSV string
        :param aggregateResults: Optional. Boolean to aggregate results
        :param availableTimeIntervals: Time interval specification (default: "all")
        :param calendarTimeIntervals: Calendar interval specification (default: "all")
        :param fields: Optional. List of fields to include in response
        :return: GetCapacityResponse instance containing capacity data with:
            - items: List of capacity data by date
            - areas: Capacity areas with calendar metrics and categories
            - calendar: Calendar time metrics (count arrays)
            - available: Available time metrics (when present)
        """
        # Build CapacityRequest object from individual parameters
        capacity_request = CapacityRequest(
            dates=dates,
            areas=areas,
            categories=categories,
            aggregateResults=aggregateResults,
            availableTimeIntervals=availableTimeIntervals,
            calendarTimeIntervals=calendarTimeIntervals,
            fields=fields
        )
        
        # Convert model to API-compatible parameters using internal converter
        params = _convert_model_to_api_params(capacity_request)
        
        # Build URL and make request
        base_url = self.baseUrl or ""
        url = urljoin(base_url, "/rest/ofscCapacity/v1/capacity")
        response = requests.get(
            url,
            headers=self.headers,
            params=params,
        )
        return response

    @wrap_return(response_type=OBJ_RESPONSE, model=GetQuotaResponse)
    def getQuota(self, 
                 dates: Union[list[str], CsvList, str],
                 areas: Optional[Union[list[str], CsvList, str]] = None,
                 categories: Optional[Union[list[str], CsvList, str]] = None,
                 aggregateResults: Optional[bool] = None,
                 categoryLevel: Optional[bool] = None,
                 intervalLevel: Optional[bool] = None,
                 returnStatuses: Optional[bool] = None,
                 timeSlotLevel: Optional[bool] = None):
        """
        Get quota information for specified areas and dates.

        This method retrieves quota information with flexible parameters that are
        converted internally to a GetQuotaRequest object.

        :param dates: Required. List of dates in YYYY-MM-DD format, CsvList, or CSV string
        :param areas: Optional. List of capacity area labels, CsvList, or CSV string
        :param categories: Optional. List of capacity categories, CsvList, or CSV string
        :param aggregateResults: Optional. Boolean to aggregate results
        :param categoryLevel: Optional. Boolean for category level reporting
        :param intervalLevel: Optional. Boolean for interval level reporting
        :param returnStatuses: Optional. Boolean for status return flag
        :param timeSlotLevel: Optional. Boolean for time slot level reporting
        :return: GetQuotaResponse instance containing quota data
        """
        # Build GetQuotaRequest object from individual parameters
        quota_request = GetQuotaRequest(
            dates=dates,
            areas=areas,
            categories=categories,
            aggregateResults=aggregateResults,
            categoryLevel=categoryLevel,
            intervalLevel=intervalLevel,
            returnStatuses=returnStatuses,
            timeSlotLevel=timeSlotLevel
        )
        
        # Convert model to API-compatible parameters using internal converter
        params = _convert_model_to_api_params(quota_request)
        
        # Build URL and make request
        base_url = self.baseUrl or ""
        url = urljoin(base_url, "/rest/ofscCapacity/v2/quota")
        response = requests.get(
            url,
            headers=self.headers,
            params=params,
        )
        return response
