"""Tests for GetActivitiesParams model."""

from datetime import date

import pytest
from pydantic import ValidationError

from ofsc.models import GetActivitiesParams


class TestGetActivitiesParamsValidation:
    """Test GetActivitiesParams validation logic."""

    def test_valid_params_with_dates_and_resources(self):
        """Test valid params with all common fields."""
        params = GetActivitiesParams(
            resources=["SUNRISE", "TECH001"],
            includeChildren="all",
            dateFrom=date(2025, 12, 1),
            dateTo=date(2025, 12, 31),
            fields=["activityId", "status", "activityType"],
            q="status=='pending'",
        )

        assert params.resources == ["SUNRISE", "TECH001"]
        assert params.dateFrom == date(2025, 12, 1)
        assert params.dateTo == date(2025, 12, 31)

    def test_valid_params_with_include_non_scheduled(self):
        """Test valid params with includeNonScheduled=True (dates not required)."""
        params = GetActivitiesParams(
            resources=["SUNRISE"],
            includeNonScheduled=True,
        )

        assert params.includeNonScheduled is True
        assert params.dateFrom is None
        assert params.dateTo is None

    def test_valid_params_with_svc_work_order_id(self):
        """Test valid params with svcWorkOrderId (dates not required)."""
        params = GetActivitiesParams(
            svcWorkOrderId=12345,
        )

        assert params.svcWorkOrderId == 12345
        assert params.dateFrom is None

    def test_invalid_date_from_without_date_to(self):
        """Test invalid: dateFrom without dateTo."""
        with pytest.raises(ValidationError) as exc_info:
            GetActivitiesParams(
                resources=["SUNRISE"],
                dateFrom=date(2025, 12, 1),
            )

        assert "dateFrom and dateTo must both be specified or both omitted" in str(
            exc_info.value
        )

    def test_invalid_date_to_without_date_from(self):
        """Test invalid: dateTo without dateFrom."""
        with pytest.raises(ValidationError) as exc_info:
            GetActivitiesParams(
                resources=["SUNRISE"],
                dateTo=date(2025, 12, 31),
            )

        assert "dateFrom and dateTo must both be specified or both omitted" in str(
            exc_info.value
        )

    def test_invalid_date_from_after_date_to(self):
        """Test invalid: dateFrom > dateTo."""
        with pytest.raises(ValidationError) as exc_info:
            GetActivitiesParams(
                resources=["SUNRISE"],
                dateFrom=date(2025, 12, 31),
                dateTo=date(2025, 12, 1),
            )

        assert "dateFrom must be before or equal to dateTo" in str(exc_info.value)

    def test_invalid_no_dates_no_svc_work_order_id_include_non_scheduled_false(self):
        """Test invalid: no dates, no svcWorkOrderId, includeNonScheduled=False."""
        with pytest.raises(ValidationError) as exc_info:
            GetActivitiesParams(
                resources=["SUNRISE"],
                includeNonScheduled=False,
            )

        assert (
            "Either dateFrom/dateTo, svcWorkOrderId, or includeNonScheduled=True is required"
            in str(exc_info.value)
        )

    def test_include_children_enum_validation(self):
        """Test includeChildren accepts only valid enum values."""
        # Valid values
        for value in ["none", "immediate", "all"]:
            params = GetActivitiesParams(
                svcWorkOrderId=12345,
                includeChildren=value,
            )
            assert params.includeChildren == value

        # Invalid value
        with pytest.raises(ValidationError):
            GetActivitiesParams(
                svcWorkOrderId=12345,
                includeChildren="invalid",
            )

    def test_extra_fields_forbidden(self):
        """Test that extra fields are not allowed."""
        with pytest.raises(ValidationError):
            GetActivitiesParams(
                resources=["SUNRISE"],
                dateFrom=date(2025, 12, 1),
                dateTo=date(2025, 12, 31),
                extraField="should fail",
            )


class TestGetActivitiesParamsToApiParams:
    """Test to_api_params() conversion method."""

    def test_to_api_params_all_fields(self):
        """Test conversion with all fields specified."""
        params = GetActivitiesParams(
            resources=["SUNRISE", "TECH001"],
            includeChildren="immediate",
            q="status=='pending'",
            dateFrom=date(2025, 12, 1),
            dateTo=date(2025, 12, 31),
            fields=["activityId", "status"],
            includeNonScheduled=True,
            svcWorkOrderId=12345,
        )

        api_params = params.to_api_params()

        assert api_params["resources"] == "SUNRISE,TECH001"
        assert api_params["includeChildren"] == "immediate"
        assert api_params["q"] == "status=='pending'"
        assert api_params["dateFrom"] == "2025-12-01"
        assert api_params["dateTo"] == "2025-12-31"
        assert api_params["fields"] == "activityId,status"
        assert api_params["includeNonScheduled"] == "true"
        assert api_params["svcWorkOrderId"] == 12345

    def test_to_api_params_minimal_fields(self):
        """Test conversion with minimal fields."""
        params = GetActivitiesParams(
            svcWorkOrderId=12345,
        )

        api_params = params.to_api_params()

        assert api_params["svcWorkOrderId"] == 12345
        # includeChildren has default "all"
        assert api_params["includeChildren"] == "all"
        # Other fields should not be in output
        assert "resources" not in api_params
        assert "dateFrom" not in api_params
        assert "q" not in api_params

    def test_to_api_params_omits_none_values(self):
        """Test that None values are not included in API params."""
        params = GetActivitiesParams(
            resources=["SUNRISE"],
            dateFrom=date(2025, 12, 1),
            dateTo=date(2025, 12, 31),
            q=None,
            fields=None,
        )

        api_params = params.to_api_params()

        assert "q" not in api_params
        assert "fields" not in api_params
        assert "resources" in api_params

    def test_to_api_params_include_non_scheduled_false_not_in_output(self):
        """Test that includeNonScheduled=False is not in output."""
        params = GetActivitiesParams(
            dateFrom=date(2025, 12, 1),
            dateTo=date(2025, 12, 31),
            includeNonScheduled=False,
        )

        api_params = params.to_api_params()

        # False should not add the parameter
        assert "includeNonScheduled" not in api_params
