"""Async version of OFSCapacity API module."""

from typing import Optional, Union

import httpx

from ..models import (
    CsvList,
    GetCapacityResponse,
    GetQuotaResponse,
    OFSConfig,
)


class AsyncOFSCapacity:
    """Async version of OFSCapacity API module."""

    def __init__(self, config: OFSConfig, client: httpx.AsyncClient):
        self._config = config
        self._client = client

    @property
    def config(self) -> OFSConfig:
        return self._config

    @property
    def baseUrl(self) -> str:
        return self._config.baseURL

    @property
    def headers(self) -> dict:
        """Build authorization headers."""
        headers = {"Content-Type": "application/json;charset=UTF-8"}
        if not self._config.useToken:
            headers["Authorization"] = "Basic " + self._config.basicAuthString.decode(
                "utf-8"
            )
        else:
            raise NotImplementedError("Token-based auth not yet implemented for async")
        return headers

    async def getAvailableCapacity(
        self,
        dates: Union[list[str], CsvList, str],
        areas: Optional[Union[list[str], CsvList, str]] = None,
        categories: Optional[Union[list[str], CsvList, str]] = None,
        aggregateResults: Optional[bool] = None,
        availableTimeIntervals: str = "all",
        calendarTimeIntervals: str = "all",
        fields: Optional[Union[list[str], CsvList, str]] = None,
    ) -> GetCapacityResponse:
        raise NotImplementedError("Async method not yet implemented")

    async def getQuota(
        self,
        dates: Union[list[str], CsvList, str],
        areas: Optional[Union[list[str], CsvList, str]] = None,
        categories: Optional[Union[list[str], CsvList, str]] = None,
        aggregateResults: Optional[bool] = None,
        categoryLevel: Optional[bool] = None,
        intervalLevel: Optional[bool] = None,
        returnStatuses: Optional[bool] = None,
        timeSlotLevel: Optional[bool] = None,
    ) -> GetQuotaResponse:
        raise NotImplementedError("Async method not yet implemented")
