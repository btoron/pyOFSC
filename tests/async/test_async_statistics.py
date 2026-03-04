"""Async tests for Statistics API operations."""

from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import (
    OFSCAuthenticationError,
    OFSCConflictError,
    OFSCValidationError,
)
from ofsc.models import (
    ActivityDurationStat,
    ActivityDurationStatRequestList,
    ActivityDurationStatsList,
    ActivityTravelStat,
    ActivityTravelStatRequestList,
    ActivityTravelStatsList,
    AirlineDistanceBasedTravel,
    AirlineDistanceBasedTravelList,
    AirlineDistanceBasedTravelRequestList,
    StatisticsPatchResponse,
)


# ---------------------------------------------------------------------------
# Activity Duration Stats
# ---------------------------------------------------------------------------


class TestAsyncGetActivityDurationStats:
    """Mocked tests for get_activity_duration_stats."""

    @pytest.mark.asyncio
    async def test_returns_model(self, mock_instance: AsyncOFSC):
        """Test that get_activity_duration_stats returns ActivityDurationStatsList."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "resourceId": "RES001",
                    "akey": "KEY1",
                    "avg": 45,
                    "dev": 5,
                    "count": 10,
                    "level": "resource",
                }
            ],
            "totalResults": 1,
            "hasMore": False,
            "offset": 0,
            "limit": 100,
        }
        mock_response.raise_for_status = Mock()
        mock_instance.statistics._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.statistics.get_activity_duration_stats()

        assert isinstance(result, ActivityDurationStatsList)
        assert len(result.items) == 1
        assert isinstance(result.items[0], ActivityDurationStat)

    @pytest.mark.asyncio
    async def test_pagination(self, mock_instance: AsyncOFSC):
        """Test that pagination params are forwarded correctly."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [],
            "totalResults": 0,
            "hasMore": False,
            "offset": 50,
            "limit": 25,
        }
        mock_response.raise_for_status = Mock()
        mock_get = AsyncMock(return_value=mock_response)
        mock_instance.statistics._client.get = mock_get

        await mock_instance.statistics.get_activity_duration_stats(offset=50, limit=25)

        call_kwargs = mock_get.call_args
        params = call_kwargs[1]["params"]
        assert params["offset"] == 50
        assert params["limit"] == 25

    @pytest.mark.asyncio
    async def test_with_resource_id(self, mock_instance: AsyncOFSC):
        """Test that optional resource_id param is forwarded."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [], "totalResults": 0}
        mock_response.raise_for_status = Mock()
        mock_get = AsyncMock(return_value=mock_response)
        mock_instance.statistics._client.get = mock_get

        await mock_instance.statistics.get_activity_duration_stats(
            resource_id="RES001", include_children=True, akey="KEY1"
        )

        params = mock_get.call_args[1]["params"]
        assert params["resourceId"] == "RES001"
        assert params["includeChildren"] == "true"
        assert params["akey"] == "KEY1"

    @pytest.mark.asyncio
    async def test_field_types(self, mock_instance: AsyncOFSC):
        """Test that fields have correct types."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "resourceId": "RES001",
                    "avg": 30,
                    "dev": 2,
                    "count": 5,
                    "level": "resource",
                }
            ],
            "totalResults": 1,
        }
        mock_response.raise_for_status = Mock()
        mock_instance.statistics._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.statistics.get_activity_duration_stats()

        item = result.items[0]
        assert isinstance(item.resourceId, str)
        assert isinstance(item.avg, int)
        assert isinstance(item.dev, int)
        assert isinstance(item.count, int)

    @pytest.mark.asyncio
    async def test_auth_error(self, mock_instance: AsyncOFSC):
        """Test that 401 raises OFSCAuthenticationError."""
        import httpx

        mock_request = Mock()
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "type": "about:blank",
            "title": "Unauthorized",
            "detail": "Authentication failed",
        }
        mock_response.text = "Unauthorized"

        http_error = httpx.HTTPStatusError(
            "401", request=mock_request, response=mock_response
        )
        mock_get = AsyncMock(side_effect=http_error)
        mock_instance.statistics._client.get = mock_get

        with pytest.raises(OFSCAuthenticationError):
            await mock_instance.statistics.get_activity_duration_stats()


# ---------------------------------------------------------------------------
# Activity Travel Stats
# ---------------------------------------------------------------------------


class TestAsyncGetActivityTravelStats:
    """Mocked tests for get_activity_travel_stats."""

    @pytest.mark.asyncio
    async def test_returns_model(self, mock_instance: AsyncOFSC):
        """Test that get_activity_travel_stats returns ActivityTravelStatsList."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "tkey": "TK1",
                    "fkey": "FK1",
                    "avg": 20,
                    "dev": 3,
                    "count": 7,
                    "region": "WEST",
                    "keyId": 42,
                    "org": ["ORG1"],
                }
            ],
            "totalResults": 1,
            "hasMore": False,
        }
        mock_response.raise_for_status = Mock()
        mock_instance.statistics._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.statistics.get_activity_travel_stats()

        assert isinstance(result, ActivityTravelStatsList)
        assert len(result.items) == 1
        assert isinstance(result.items[0], ActivityTravelStat)

    @pytest.mark.asyncio
    async def test_pagination(self, mock_instance: AsyncOFSC):
        """Test pagination params forwarded for travel stats."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [], "totalResults": 0}
        mock_response.raise_for_status = Mock()
        mock_get = AsyncMock(return_value=mock_response)
        mock_instance.statistics._client.get = mock_get

        await mock_instance.statistics.get_activity_travel_stats(offset=10, limit=50)

        params = mock_get.call_args[1]["params"]
        assert params["offset"] == 10
        assert params["limit"] == 50

    @pytest.mark.asyncio
    async def test_with_optional_params(self, mock_instance: AsyncOFSC):
        """Test that optional params are forwarded for travel stats."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [], "totalResults": 0}
        mock_response.raise_for_status = Mock()
        mock_get = AsyncMock(return_value=mock_response)
        mock_instance.statistics._client.get = mock_get

        await mock_instance.statistics.get_activity_travel_stats(
            region="WEST", tkey="TK1", fkey="FK1", key_id=42
        )

        params = mock_get.call_args[1]["params"]
        assert params["region"] == "WEST"
        assert params["tkey"] == "TK1"
        assert params["fkey"] == "FK1"
        assert params["keyId"] == 42

    @pytest.mark.asyncio
    async def test_field_types(self, mock_instance: AsyncOFSC):
        """Test that fields have correct types for travel stats."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "tkey": "TK1",
                    "fkey": "FK1",
                    "avg": 15,
                    "count": 3,
                    "keyId": 10,
                    "org": ["A", "B"],
                }
            ],
            "totalResults": 1,
        }
        mock_response.raise_for_status = Mock()
        mock_instance.statistics._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.statistics.get_activity_travel_stats()

        item = result.items[0]
        assert isinstance(item.tkey, str)
        assert isinstance(item.avg, int)
        assert isinstance(item.keyId, int)
        assert isinstance(item.org, list)

    @pytest.mark.asyncio
    async def test_auth_error(self, mock_instance: AsyncOFSC):
        """Test that 401 raises OFSCAuthenticationError for travel stats."""
        import httpx

        mock_request = Mock()
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "type": "about:blank",
            "title": "Unauthorized",
            "detail": "Authentication failed",
        }
        mock_response.text = "Unauthorized"

        http_error = httpx.HTTPStatusError(
            "401", request=mock_request, response=mock_response
        )
        mock_instance.statistics._client.get = AsyncMock(side_effect=http_error)

        with pytest.raises(OFSCAuthenticationError):
            await mock_instance.statistics.get_activity_travel_stats()


# ---------------------------------------------------------------------------
# Airline Distance Based Travel
# ---------------------------------------------------------------------------


class TestAsyncGetAirlineDistanceBasedTravel:
    """Mocked tests for get_airline_distance_based_travel."""

    @pytest.mark.asyncio
    async def test_returns_model(self, mock_instance: AsyncOFSC):
        """Test that get_airline_distance_based_travel returns AirlineDistanceBasedTravelList."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "level": "region",
                    "key": "WEST",
                    "keyId": 1,
                    "org": ["ORG1"],
                    "data": [
                        {"distance": 10, "estimated": 15, "override": None},
                        {"distance": 20, "estimated": 25},
                    ],
                }
            ],
            "totalResults": 1,
            "hasMore": False,
        }
        mock_response.raise_for_status = Mock()
        mock_instance.statistics._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.statistics.get_airline_distance_based_travel()

        assert isinstance(result, AirlineDistanceBasedTravelList)
        assert len(result.items) == 1
        assert isinstance(result.items[0], AirlineDistanceBasedTravel)
        assert len(result.items[0].data) == 2

    @pytest.mark.asyncio
    async def test_pagination(self, mock_instance: AsyncOFSC):
        """Test pagination params forwarded for airline distance travel."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [], "totalResults": 0}
        mock_response.raise_for_status = Mock()
        mock_get = AsyncMock(return_value=mock_response)
        mock_instance.statistics._client.get = mock_get

        await mock_instance.statistics.get_airline_distance_based_travel(
            offset=20, limit=10
        )

        params = mock_get.call_args[1]["params"]
        assert params["offset"] == 20
        assert params["limit"] == 10

    @pytest.mark.asyncio
    async def test_with_optional_params(self, mock_instance: AsyncOFSC):
        """Test that optional params are forwarded for airline distance travel."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [], "totalResults": 0}
        mock_response.raise_for_status = Mock()
        mock_get = AsyncMock(return_value=mock_response)
        mock_instance.statistics._client.get = mock_get

        await mock_instance.statistics.get_airline_distance_based_travel(
            level="region", key="WEST", distance=50, key_id=1
        )

        params = mock_get.call_args[1]["params"]
        assert params["level"] == "region"
        assert params["key"] == "WEST"
        assert params["distance"] == 50
        assert params["keyId"] == 1

    @pytest.mark.asyncio
    async def test_field_types(self, mock_instance: AsyncOFSC):
        """Test that fields have correct types for airline distance travel."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "level": "resource",
                    "key": "R001",
                    "keyId": 5,
                    "data": [{"distance": 10, "estimated": 12}],
                }
            ],
            "totalResults": 1,
        }
        mock_response.raise_for_status = Mock()
        mock_instance.statistics._client.get = AsyncMock(return_value=mock_response)

        result = await mock_instance.statistics.get_airline_distance_based_travel()

        item = result.items[0]
        assert isinstance(item.level, str)
        assert isinstance(item.key, str)
        assert isinstance(item.keyId, int)
        assert isinstance(item.data, list)
        assert item.data[0].distance == 10
        assert item.data[0].estimated == 12

    @pytest.mark.asyncio
    async def test_auth_error(self, mock_instance: AsyncOFSC):
        """Test that 401 raises OFSCAuthenticationError for airline distance travel."""
        import httpx

        mock_request = Mock()
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "type": "about:blank",
            "title": "Unauthorized",
            "detail": "Authentication failed",
        }
        mock_response.text = "Unauthorized"

        http_error = httpx.HTTPStatusError(
            "401", request=mock_request, response=mock_response
        )
        mock_instance.statistics._client.get = AsyncMock(side_effect=http_error)

        with pytest.raises(OFSCAuthenticationError):
            await mock_instance.statistics.get_airline_distance_based_travel()


# ---------------------------------------------------------------------------
# Model Validation Tests (no async, no API)
# ---------------------------------------------------------------------------


class TestAsyncStatisticsModelValidation:
    """Pure model validation tests."""

    def test_activity_duration_stat_model(self):
        """Test ActivityDurationStat model validation."""
        data = {
            "resourceId": "R001",
            "akey": "INSTALL",
            "avg": 60,
            "dev": 10,
            "count": 100,
            "level": "resource",
        }
        stat = ActivityDurationStat.model_validate(data)
        assert stat.resourceId == "R001"
        assert stat.avg == 60
        assert stat.count == 100

    def test_activity_duration_stat_all_optional(self):
        """Test that ActivityDurationStat accepts empty dict."""
        stat = ActivityDurationStat.model_validate({})
        assert stat.resourceId is None
        assert stat.avg is None

    def test_activity_duration_stats_list_model(self):
        """Test ActivityDurationStatsList model validation."""
        data = {
            "items": [{"resourceId": "R1", "avg": 30}, {"resourceId": "R2", "avg": 45}],
            "totalResults": 2,
            "hasMore": False,
            "offset": 0,
            "limit": 100,
        }
        result = ActivityDurationStatsList.model_validate(data)
        assert isinstance(result, ActivityDurationStatsList)
        assert len(result.items) == 2
        assert result.totalResults == 2

    def test_activity_travel_stat_model(self):
        """Test ActivityTravelStat model validation."""
        data = {
            "tkey": "TK1",
            "fkey": "FK1",
            "avg": 20,
            "dev": 3,
            "count": 50,
            "region": "WEST",
            "keyId": 10,
            "org": ["ORG1", "ORG2"],
        }
        stat = ActivityTravelStat.model_validate(data)
        assert stat.tkey == "TK1"
        assert stat.region == "WEST"
        assert stat.org == ["ORG1", "ORG2"]

    def test_activity_travel_stats_list_model(self):
        """Test ActivityTravelStatsList model validation."""
        data = {
            "items": [{"tkey": "T1", "avg": 10}],
            "totalResults": 1,
        }
        result = ActivityTravelStatsList.model_validate(data)
        assert isinstance(result, ActivityTravelStatsList)
        assert len(result.items) == 1

    def test_airline_distance_data_model(self):
        """Test AirlineDistanceData model validation."""
        from ofsc.models import AirlineDistanceData

        data = {"distance": 15, "estimated": 18, "override": 20}
        item = AirlineDistanceData.model_validate(data)
        assert item.distance == 15
        assert item.estimated == 18
        assert item.override == 20

    def test_airline_distance_based_travel_model(self):
        """Test AirlineDistanceBasedTravel model validation."""
        data = {
            "level": "region",
            "key": "WEST",
            "keyId": 1,
            "org": ["ORG1"],
            "data": [{"distance": 10, "estimated": 12}],
        }
        item = AirlineDistanceBasedTravel.model_validate(data)
        assert item.level == "region"
        assert item.key == "WEST"
        assert len(item.data) == 1

    def test_airline_distance_based_travel_list_model(self):
        """Test AirlineDistanceBasedTravelList model validation."""
        data = {
            "items": [
                {
                    "level": "resource",
                    "key": "R001",
                    "data": [{"distance": 5, "estimated": 6}],
                }
            ],
            "totalResults": 1,
        }
        result = AirlineDistanceBasedTravelList.model_validate(data)
        assert isinstance(result, AirlineDistanceBasedTravelList)
        assert len(result.items) == 1
        assert result.items[0].key == "R001"

    def test_empty_items_list(self):
        """Test that empty items list is valid for all list models."""
        for model_cls in [
            ActivityDurationStatsList,
            ActivityTravelStatsList,
            AirlineDistanceBasedTravelList,
        ]:
            result = model_cls.model_validate({"items": [], "totalResults": 0})
            assert result.items == []
            assert result.totalResults == 0


# ---------------------------------------------------------------------------
# Live Tests
# ---------------------------------------------------------------------------


class TestAsyncStatisticsLive:
    """Live tests against the actual OFSC API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_activity_duration_stats(self, async_instance: AsyncOFSC):
        """Test get_activity_duration_stats with actual API."""
        result = await async_instance.statistics.get_activity_duration_stats(limit=10)
        assert isinstance(result, ActivityDurationStatsList)
        assert isinstance(result.items, list)
        assert result.totalResults >= 0

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_activity_travel_stats(self, async_instance: AsyncOFSC):
        """Test get_activity_travel_stats with actual API."""
        result = await async_instance.statistics.get_activity_travel_stats(limit=10)
        assert isinstance(result, ActivityTravelStatsList)
        assert isinstance(result.items, list)
        assert result.totalResults >= 0

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_airline_distance_based_travel(self, async_instance: AsyncOFSC):
        """Test get_airline_distance_based_travel with actual API."""
        result = await async_instance.statistics.get_airline_distance_based_travel(
            limit=10
        )
        assert isinstance(result, AirlineDistanceBasedTravelList)
        assert isinstance(result.items, list)
        assert result.totalResults >= 0


# ---------------------------------------------------------------------------
# Update Activity Duration Stats (PATCH)
# ---------------------------------------------------------------------------


def _make_mock_patch_response(status_code: int = 200, updated: int = 1):
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = {"status": "200", "updatedRecords": updated}
    mock_response.raise_for_status = Mock()
    return mock_response


class TestAsyncUpdateActivityDurationStats:
    """Mocked tests for update_activity_duration_stats."""

    @pytest.mark.asyncio
    async def test_returns_model(self, mock_instance: AsyncOFSC):
        """Test that update_activity_duration_stats returns StatisticsPatchResponse."""
        mock_response = _make_mock_patch_response()
        mock_instance.statistics._client.patch = AsyncMock(return_value=mock_response)

        request_data = ActivityDurationStatRequestList(
            items=[{"resourceId": "RES001", "akey": "INSTALL", "override": 60}]
        )
        result = await mock_instance.statistics.update_activity_duration_stats(
            request_data
        )

        assert isinstance(result, StatisticsPatchResponse)
        assert result.updatedRecords == 1

    @pytest.mark.asyncio
    async def test_with_model_input(self, mock_instance: AsyncOFSC):
        """Test that model input is accepted and serialized correctly."""
        mock_response = _make_mock_patch_response()
        mock_patch = AsyncMock(return_value=mock_response)
        mock_instance.statistics._client.patch = mock_patch

        request_data = ActivityDurationStatRequestList(
            items=[{"resourceId": "", "akey": "REPAIR", "override": 120}]
        )
        await mock_instance.statistics.update_activity_duration_stats(request_data)

        call_kwargs = mock_patch.call_args[1]
        assert "json" in call_kwargs
        assert call_kwargs["json"]["items"][0]["akey"] == "REPAIR"

    @pytest.mark.asyncio
    async def test_with_dict_input(self, mock_instance: AsyncOFSC):
        """Test that raw dict input is accepted."""
        mock_response = _make_mock_patch_response()
        mock_instance.statistics._client.patch = AsyncMock(return_value=mock_response)

        result = await mock_instance.statistics.update_activity_duration_stats(
            {"items": [{"resourceId": "R1", "akey": "VISIT", "override": 30}]}
        )

        assert isinstance(result, StatisticsPatchResponse)

    @pytest.mark.asyncio
    async def test_auth_error(self, mock_instance: AsyncOFSC):
        """Test that 401 raises OFSCAuthenticationError."""
        import httpx

        mock_request = Mock()
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Unauthorized"}
        mock_response.text = "Unauthorized"
        http_error = httpx.HTTPStatusError(
            "401", request=mock_request, response=mock_response
        )
        mock_instance.statistics._client.patch = AsyncMock(side_effect=http_error)

        with pytest.raises(OFSCAuthenticationError):
            await mock_instance.statistics.update_activity_duration_stats(
                {"items": [{"resourceId": "", "akey": "X", "override": 0}]}
            )

    @pytest.mark.asyncio
    async def test_validation_error(self, mock_instance: AsyncOFSC):
        """Test that 400 raises OFSCValidationError."""
        import httpx

        mock_request = Mock()
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Bad request"}
        mock_response.text = "Bad request"
        http_error = httpx.HTTPStatusError(
            "400", request=mock_request, response=mock_response
        )
        mock_instance.statistics._client.patch = AsyncMock(side_effect=http_error)

        with pytest.raises(OFSCValidationError):
            await mock_instance.statistics.update_activity_duration_stats(
                {"items": [{"resourceId": "", "akey": "X", "override": 0}]}
            )


# ---------------------------------------------------------------------------
# Update Activity Travel Stats (PATCH)
# ---------------------------------------------------------------------------


class TestAsyncUpdateActivityTravelStats:
    """Mocked tests for update_activity_travel_stats."""

    @pytest.mark.asyncio
    async def test_returns_model(self, mock_instance: AsyncOFSC):
        """Test that update_activity_travel_stats returns StatisticsPatchResponse."""
        mock_response = _make_mock_patch_response()
        mock_instance.statistics._client.patch = AsyncMock(return_value=mock_response)

        request_data = ActivityTravelStatRequestList(
            items=[{"fkey": "FK1", "tkey": "TK1", "override": 15}]
        )
        result = await mock_instance.statistics.update_activity_travel_stats(
            request_data
        )

        assert isinstance(result, StatisticsPatchResponse)
        assert result.updatedRecords == 1

    @pytest.mark.asyncio
    async def test_with_dict_input(self, mock_instance: AsyncOFSC):
        """Test that raw dict input is accepted."""
        mock_response = _make_mock_patch_response()
        mock_instance.statistics._client.patch = AsyncMock(return_value=mock_response)

        result = await mock_instance.statistics.update_activity_travel_stats(
            {"items": [{"fkey": "A", "tkey": "B", "override": 5}]}
        )

        assert isinstance(result, StatisticsPatchResponse)

    @pytest.mark.asyncio
    async def test_with_optional_key_id(self, mock_instance: AsyncOFSC):
        """Test that optional keyId is serialized when provided."""
        mock_response = _make_mock_patch_response()
        mock_patch = AsyncMock(return_value=mock_response)
        mock_instance.statistics._client.patch = mock_patch

        request_data = ActivityTravelStatRequestList(
            items=[{"fkey": "FK1", "tkey": "TK1", "override": 10, "keyId": 42}]
        )
        await mock_instance.statistics.update_activity_travel_stats(request_data)

        call_kwargs = mock_patch.call_args[1]
        assert call_kwargs["json"]["items"][0]["keyId"] == 42

    @pytest.mark.asyncio
    async def test_conflict_error(self, mock_instance: AsyncOFSC):
        """Test that 409 raises OFSCConflictError."""
        import httpx

        mock_request = Mock()
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 409
        mock_response.json.return_value = {
            "detail": "Detect activity travel keys automatically is enabled"
        }
        mock_response.text = "Conflict"
        http_error = httpx.HTTPStatusError(
            "409", request=mock_request, response=mock_response
        )
        mock_instance.statistics._client.patch = AsyncMock(side_effect=http_error)

        with pytest.raises(OFSCConflictError):
            await mock_instance.statistics.update_activity_travel_stats(
                {"items": [{"fkey": "A", "tkey": "B", "override": 5}]}
            )

    @pytest.mark.asyncio
    async def test_auth_error(self, mock_instance: AsyncOFSC):
        """Test that 401 raises OFSCAuthenticationError."""
        import httpx

        mock_request = Mock()
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Unauthorized"}
        mock_response.text = "Unauthorized"
        http_error = httpx.HTTPStatusError(
            "401", request=mock_request, response=mock_response
        )
        mock_instance.statistics._client.patch = AsyncMock(side_effect=http_error)

        with pytest.raises(OFSCAuthenticationError):
            await mock_instance.statistics.update_activity_travel_stats(
                {"items": [{"fkey": "A", "tkey": "B", "override": 5}]}
            )


# ---------------------------------------------------------------------------
# Update Airline Distance Based Travel (PATCH)
# ---------------------------------------------------------------------------


class TestAsyncUpdateAirlineDistanceBasedTravel:
    """Mocked tests for update_airline_distance_based_travel."""

    @pytest.mark.asyncio
    async def test_returns_model(self, mock_instance: AsyncOFSC):
        """Test that update_airline_distance_based_travel returns StatisticsPatchResponse."""
        mock_response = _make_mock_patch_response()
        mock_instance.statistics._client.patch = AsyncMock(return_value=mock_response)

        request_data = AirlineDistanceBasedTravelRequestList(
            items=[{"data": [{"distance": 10, "override": 12}]}]
        )
        result = await mock_instance.statistics.update_airline_distance_based_travel(
            request_data
        )

        assert isinstance(result, StatisticsPatchResponse)
        assert result.updatedRecords == 1

    @pytest.mark.asyncio
    async def test_with_dict_input(self, mock_instance: AsyncOFSC):
        """Test that raw dict input is accepted."""
        mock_response = _make_mock_patch_response()
        mock_instance.statistics._client.patch = AsyncMock(return_value=mock_response)

        result = await mock_instance.statistics.update_airline_distance_based_travel(
            {"items": [{"data": [{"distance": 5, "override": 6}], "key": "WEST"}]}
        )

        assert isinstance(result, StatisticsPatchResponse)

    @pytest.mark.asyncio
    async def test_with_optional_fields(self, mock_instance: AsyncOFSC):
        """Test that optional key/keyId/level fields are serialized."""
        mock_response = _make_mock_patch_response()
        mock_patch = AsyncMock(return_value=mock_response)
        mock_instance.statistics._client.patch = mock_patch

        request_data = AirlineDistanceBasedTravelRequestList(
            items=[
                {
                    "data": [{"distance": 10, "override": 15}],
                    "key": "WEST",
                    "keyId": 7,
                    "level": "travelkey",
                }
            ]
        )
        await mock_instance.statistics.update_airline_distance_based_travel(
            request_data
        )

        call_kwargs = mock_patch.call_args[1]
        item = call_kwargs["json"]["items"][0]
        assert item["key"] == "WEST"
        assert item["keyId"] == 7
        assert item["level"] == "travelkey"

    @pytest.mark.asyncio
    async def test_conflict_error(self, mock_instance: AsyncOFSC):
        """Test that 409 raises OFSCConflictError."""
        import httpx

        mock_request = Mock()
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 409
        mock_response.json.return_value = {"detail": "Auto-detect is enabled"}
        mock_response.text = "Conflict"
        http_error = httpx.HTTPStatusError(
            "409", request=mock_request, response=mock_response
        )
        mock_instance.statistics._client.patch = AsyncMock(side_effect=http_error)

        with pytest.raises(OFSCConflictError):
            await mock_instance.statistics.update_airline_distance_based_travel(
                {"items": [{"data": [{"distance": 5, "override": 6}]}]}
            )

    @pytest.mark.asyncio
    async def test_auth_error(self, mock_instance: AsyncOFSC):
        """Test that 401 raises OFSCAuthenticationError."""
        import httpx

        mock_request = Mock()
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Unauthorized"}
        mock_response.text = "Unauthorized"
        http_error = httpx.HTTPStatusError(
            "401", request=mock_request, response=mock_response
        )
        mock_instance.statistics._client.patch = AsyncMock(side_effect=http_error)

        with pytest.raises(OFSCAuthenticationError):
            await mock_instance.statistics.update_airline_distance_based_travel(
                {"items": [{"data": [{"distance": 5, "override": 6}]}]}
            )


# ---------------------------------------------------------------------------
# Write Model Validation Tests
# ---------------------------------------------------------------------------


class TestStatisticsWriteModelValidation:
    """Pure model validation tests for write request/response models."""

    def test_statistics_patch_response_model(self):
        """Test StatisticsPatchResponse model validation."""
        data = {"status": "200", "updatedRecords": 5}
        result = StatisticsPatchResponse.model_validate(data)
        assert isinstance(result, StatisticsPatchResponse)
        assert result.status == "200"
        assert result.updatedRecords == 5

    def test_statistics_patch_response_empty(self):
        """Test StatisticsPatchResponse with empty results."""
        result = StatisticsPatchResponse.model_validate({})
        assert result.updatedRecords is None

    def test_activity_duration_stat_request_model(self):
        """Test ActivityDurationStatRequest required fields."""
        from ofsc.models import ActivityDurationStatRequest

        req = ActivityDurationStatRequest(akey="INSTALL", override=60)
        assert req.resourceId == ""
        assert req.akey == "INSTALL"
        assert req.override == 60

    def test_activity_duration_stat_request_list_model(self):
        """Test ActivityDurationStatRequestList model validation."""
        data = {
            "items": [
                {"resourceId": "R1", "akey": "INSTALL", "override": 60},
                {"resourceId": "", "akey": "REPAIR", "override": 0},
            ]
        }
        result = ActivityDurationStatRequestList.model_validate(data)
        assert len(result.items) == 2
        assert result.items[0].resourceId == "R1"

    def test_activity_travel_stat_request_model(self):
        """Test ActivityTravelStatRequest required and optional fields."""
        from ofsc.models import ActivityTravelStatRequest

        req = ActivityTravelStatRequest(fkey="FK1", tkey="TK1", override=15)
        assert req.fkey == "FK1"
        assert req.tkey == "TK1"
        assert req.override == 15
        assert req.keyId is None

    def test_activity_travel_stat_request_with_key_id(self):
        """Test ActivityTravelStatRequest with optional keyId."""
        from ofsc.models import ActivityTravelStatRequest

        req = ActivityTravelStatRequest(fkey="FK1", tkey="TK1", override=15, keyId=42)
        assert req.keyId == 42

    def test_airline_distance_override_data_model(self):
        """Test AirlineDistanceOverrideData model validation."""
        from ofsc.models import AirlineDistanceOverrideData

        data = AirlineDistanceOverrideData(distance=10, override=12)
        assert data.distance == 10
        assert data.override == 12

    def test_airline_distance_based_travel_request_model(self):
        """Test AirlineDistanceBasedTravelRequest model validation."""
        from ofsc.models import AirlineDistanceBasedTravelRequest

        req = AirlineDistanceBasedTravelRequest(
            data=[{"distance": 10, "override": 12}],
            key="WEST",
            keyId=7,
            level="travelkey",
        )
        assert len(req.data) == 1
        assert req.key == "WEST"
        assert req.keyId == 7
        assert req.level == "travelkey"

    def test_airline_distance_based_travel_request_optional_fields(self):
        """Test AirlineDistanceBasedTravelRequest with only required fields."""
        from ofsc.models import AirlineDistanceBasedTravelRequest

        req = AirlineDistanceBasedTravelRequest(data=[{"distance": 5, "override": 6}])
        assert req.key is None
        assert req.keyId is None
        assert req.level is None


# ---------------------------------------------------------------------------
# Live Write (Roundtrip) Tests
# ---------------------------------------------------------------------------


class TestAsyncStatisticsWriteLive:
    """Live roundtrip tests against the actual OFSC API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_activity_duration_stats_roundtrip(self, async_instance: AsyncOFSC):
        """Test roundtrip: GET current stats, PATCH override, PATCH back."""
        stats = await async_instance.statistics.get_activity_duration_stats(limit=1)
        if not stats.items:
            pytest.skip("No activity duration stats available")

        first = stats.items[0]
        resource_id = first.resourceId or ""
        akey = first.akey or ""

        result = await async_instance.statistics.update_activity_duration_stats(
            ActivityDurationStatRequestList(
                items=[{"resourceId": resource_id, "akey": akey, "override": 30}]
            )
        )
        assert isinstance(result, StatisticsPatchResponse)
        assert result.updatedRecords is not None
        assert result.updatedRecords >= 1

        # Reset override back to learned (0 means use learned value)
        reset = await async_instance.statistics.update_activity_duration_stats(
            ActivityDurationStatRequestList(
                items=[{"resourceId": resource_id, "akey": akey, "override": 0}]
            )
        )
        assert isinstance(reset, StatisticsPatchResponse)

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_activity_travel_stats_roundtrip(self, async_instance: AsyncOFSC):
        """Test roundtrip: GET current travel stats, PATCH override, PATCH back."""
        stats = await async_instance.statistics.get_activity_travel_stats(limit=1)
        if not stats.items:
            pytest.skip("No activity travel stats available")

        first = stats.items[0]
        fkey = first.fkey or ""
        tkey = first.tkey or ""

        try:
            result = await async_instance.statistics.update_activity_travel_stats(
                ActivityTravelStatRequestList(
                    items=[{"fkey": fkey, "tkey": tkey, "override": 10}]
                )
            )
            assert isinstance(result, StatisticsPatchResponse)
            assert result.updatedRecords is not None

            reset = await async_instance.statistics.update_activity_travel_stats(
                ActivityTravelStatRequestList(
                    items=[{"fkey": fkey, "tkey": tkey, "override": 0}]
                )
            )
            assert isinstance(reset, StatisticsPatchResponse)
        except OFSCConflictError:
            pytest.skip(
                "Auto-detect travel keys is enabled; manual overrides not allowed"
            )

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_airline_distance_based_travel_roundtrip(
        self, async_instance: AsyncOFSC
    ):
        """Test roundtrip: GET current airline distance data, PATCH, PATCH back."""
        data = await async_instance.statistics.get_airline_distance_based_travel(
            limit=1
        )
        if not data.items:
            pytest.skip("No airline distance based travel data available")

        first = data.items[0]
        if not first.data or len(first.data) < 2:
            pytest.skip("First item needs at least 2 distance data points")

        # Company level requires exactly 2 data points per request
        dp0 = first.data[0]
        dp1 = first.data[1]
        original_override = dp0.override

        try:
            # Modify first point's override by +1 to keep values reasonable
            result = (
                await async_instance.statistics.update_airline_distance_based_travel(
                    AirlineDistanceBasedTravelRequestList(
                        items=[
                            {
                                "data": [
                                    {
                                        "distance": dp0.distance,
                                        "override": dp0.override + 1,
                                    },
                                    {
                                        "distance": dp1.distance,
                                        "override": dp1.override,
                                    },
                                ],
                                "key": first.key,
                                "keyId": first.keyId,
                                "level": first.level,
                            }
                        ]
                    )
                )
            )
            assert isinstance(result, StatisticsPatchResponse)

            # Restore original values
            reset = (
                await async_instance.statistics.update_airline_distance_based_travel(
                    AirlineDistanceBasedTravelRequestList(
                        items=[
                            {
                                "data": [
                                    {
                                        "distance": dp0.distance,
                                        "override": original_override,
                                    },
                                    {
                                        "distance": dp1.distance,
                                        "override": dp1.override,
                                    },
                                ],
                                "key": first.key,
                                "keyId": first.keyId,
                                "level": first.level,
                            }
                        ]
                    )
                )
            )
            assert isinstance(reset, StatisticsPatchResponse)
        except OFSCConflictError:
            pytest.skip(
                "Auto-detect travel keys is enabled; manual overrides not allowed"
            )
