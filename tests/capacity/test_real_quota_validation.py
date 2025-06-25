"""
Test to validate QuotaResponse models against real API response data
"""

import json
from pathlib import Path

from ofsc.models import GetQuotaResponse


def test_real_quota_json_validation():
    """Test that the updated QuotaResponse models can parse the real JSON data"""

    # Read the real JSON file
    json_file = Path(__file__).parent / "_REAL_get_quota.json"
    with open(json_file, "r") as f:
        json_data = json.load(f)

    # Validate against GetQuotaResponse model
    response = GetQuotaResponse.model_validate(json_data)

    # Basic structure validation
    assert response.items is not None
    assert len(response.items) > 0

    # Check first item structure
    first_item = response.items[0]
    assert first_item.date == "2025-06-25"
    assert first_item.areas is not None
    assert len(first_item.areas) > 0

    # Check first area structure
    first_area = first_item.areas[0]
    assert first_area.label is not None
    assert first_area.name is not None

    # Check that new fields are present
    assert hasattr(first_area, "quotaIsClosed")
    assert hasattr(first_area, "quotaIsAutoClosed")
    assert hasattr(first_area, "intervals")
    assert hasattr(first_area, "categories")

    # Check data types for percentage fields (should be float)
    if first_area.quotaPercent is not None:
        assert isinstance(first_area.quotaPercent, (int, float))
    if first_area.usedQuotaPercent is not None:
        assert isinstance(first_area.usedQuotaPercent, (int, float))

    # Check intervals structure if present
    if first_area.intervals:
        first_interval = first_area.intervals[0]
        assert hasattr(first_interval, "timeFrom")
        assert hasattr(first_interval, "timeTo")
        assert hasattr(first_interval, "quotaIsClosed")
        assert hasattr(first_interval, "quotaIsAutoClosed")

        # Validate time format
        assert isinstance(first_interval.timeFrom, str)
        assert isinstance(first_interval.timeTo, str)
        assert ":" in first_interval.timeFrom
        assert ":" in first_interval.timeTo

    # Check categories structure if present
    if first_area.categories:
        first_category = first_area.categories[0]
        assert hasattr(first_category, "label")
        assert hasattr(first_category, "quotaPercentDay")
        assert hasattr(first_category, "quotaPercentCategory")
        assert hasattr(first_category, "intervals")

        # Check float types for category percentages
        if first_category.quotaPercentDay is not None:
            assert isinstance(first_category.quotaPercentDay, (int, float))
        if first_category.quotaPercentCategory is not None:
            assert isinstance(first_category.quotaPercentCategory, (int, float))
        if first_category.usedQuotaPercent is not None:
            assert isinstance(first_category.usedQuotaPercent, (int, float))

        # Check category intervals if present
        if first_category.intervals:
            cat_interval = first_category.intervals[0]
            assert hasattr(cat_interval, "timeFrom")
            assert hasattr(cat_interval, "timeTo")
            assert hasattr(cat_interval, "quota")
            assert hasattr(cat_interval, "used")


def test_quota_model_fields_coverage():
    """Test that all fields from real data are covered by the models"""

    # Read the real JSON file
    json_file = Path(__file__).parent / "REAL_get_quota.json"
    with open(json_file, "r") as f:
        json_data = json.load(f)

    # Parse successfully (this will fail if any required fields are missing)
    response = GetQuotaResponse.model_validate(json_data)

    # Check specific values to ensure proper parsing
    first_area = response.items[0].areas[0]

    # Verify boolean fields are properly parsed
    assert isinstance(first_area.quotaIsClosed, bool)
    assert isinstance(first_area.quotaIsAutoClosed, bool)

    # Verify float fields handle decimal values
    if first_area.usedQuotaPercent is not None:
        # The real data has values like 101.5
        assert first_area.usedQuotaPercent >= 0

    # Check that we can access nested structures without errors
    if first_area.categories:
        category = first_area.categories[0]
        if category.quotaPercentDay is not None:
            # The real data has values like 95.03
            assert category.quotaPercentDay >= 0

        if category.intervals:
            interval = category.intervals[0]
            assert interval.timeFrom is not None
            assert interval.timeTo is not None


if __name__ == "__main__":
    test_real_quota_json_validation()
    test_quota_model_fields_coverage()
    print("All quota model validation tests passed!")
