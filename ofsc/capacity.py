from urllib.parse import urljoin

import requests

from ofsc.models import OFSApi

from .common import OBJ_RESPONSE, wrap_return
from .models import CapacityRequest, GetCapacityResponse


class OFSCapacity(OFSApi):
    # OFSC Function Library

    @wrap_return(response_type=OBJ_RESPONSE, model=GetCapacityResponse)
    def getAvailableCapacity(self, request: CapacityRequest):
        """
        Get available capacity for a given resource or group of resources.

        This method retrieves capacity information including calendar time and available time
        for specified capacity areas and date ranges. The response includes metrics by area
        and optionally by category.

        :param request: CapacityRequest object containing:
            - areas: List of capacity area labels to query
            - dates: List of dates in YYYY-MM-DD format
            - categories: Optional list of capacity categories to filter by
            - aggregateResults: Optional boolean to aggregate results
            - availableTimeIntervals: Time interval specification (default: "all")
            - calendarTimeIntervals: Calendar interval specification (default: "all")
            - fields: Optional list of fields to include in response
        :return: GetCapacityResponse instance containing capacity data with:
            - items: List of capacity data by date
            - areas: Capacity areas with calendar metrics and categories
            - calendar: Calendar time metrics (count arrays)
            - available: Available time metrics (when present)
        """
        params = request.model_dump(exclude_none=True)
        base_url = self.baseUrl or ""
        url = urljoin(base_url, "/rest/ofscCapacity/v1/capacity")
        response = requests.get(
            url,
            headers=self.headers,
            params=params,
        )
        return response
