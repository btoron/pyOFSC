"""Validation tests for quota-related models in OFSC v3.0."""

import pytest
from pydantic import ValidationError

from ofsc.models.capacity import (
    GetQuotaRequest,
    GetQuotaResponse,
    QuotaTimeInterval,
    QuotaCategoryItem,
    QuotaAreaItem,
    QuotaResponseItem,
)
from ofsc.models.base import BaseOFSResponse


class TestQuotaModelsValidation:
    """Test validation for quota-related models."""

    def test_get_quota_request_validation(self):
        """Test GetQuotaRequest model validation."""
        # Test minimal valid request
        request = GetQuotaRequest(dates=["2024-01-15"], areas=["AREA1", "AREA2"])

        assert request.dates.to_list() == ["2024-01-15"]
        assert request.areas.to_list() == ["AREA1", "AREA2"]
        assert request.categories is None
        assert request.intervalLevel is None

        # Test with all fields
        full_request = GetQuotaRequest(
            dates=["2024-01-15"],
            areas=["AREA1", "AREA2"],
            categories=["CAT1", "CAT2"],
            intervalLevel=True,
        )

        assert full_request.categories.to_list() == ["CAT1", "CAT2"]
        assert full_request.intervalLevel is True

    def test_get_quota_request_required_fields(self):
        """Test GetQuotaRequest required field validation."""
        # Missing dates should raise validation error
        with pytest.raises(ValueError, match="Field required"):
            GetQuotaRequest(areas=["AREA1"])

        # dates is required, areas is optional
        request = GetQuotaRequest(dates=["2024-01-15"])
        assert request.dates.to_list() == ["2024-01-15"]
        assert request.areas is None

    def test_quota_time_interval_validation(self):
        """Test QuotaTimeInterval model validation."""
        interval = QuotaTimeInterval(
            timeFrom="08:00", timeTo="17:00", quota=100, used=25
        )

        assert interval.timeFrom == "08:00"
        assert interval.timeTo == "17:00"
        assert interval.quota == 100
        assert interval.used == 25

    def test_quota_time_interval_optional_fields(self):
        """Test QuotaTimeInterval with optional fields."""
        # Test minimal interval - timeFrom and timeTo are required
        with pytest.raises(ValueError, match="Field required"):
            QuotaTimeInterval()

        # Test with required fields only
        minimal = QuotaTimeInterval(timeFrom="08:00", timeTo="17:00")
        assert minimal.timeFrom == "08:00"
        assert minimal.timeTo == "17:00"
        assert minimal.quota is None
        assert minimal.used is None

    def test_quota_category_item_validation(self):
        """Test QuotaCategoryItem model validation."""
        category_item = QuotaCategoryItem(
            categoryLabel="Installation",
            workSkillLabel="Electrical",
            totalQuota=50,
            usedQuota=12,
            availableQuota=38,
            timeIntervals=[
                QuotaTimeInterval(timeFrom="09:00", timeTo="12:00", quota=25)
            ],
        )

        assert category_item.categoryLabel == "Installation"
        assert category_item.workSkillLabel == "Electrical"
        assert category_item.totalQuota == 50
        assert category_item.usedQuota == 12
        assert category_item.availableQuota == 38
        assert len(category_item.timeIntervals) == 1
        assert category_item.timeIntervals[0].timeFrom == "09:00"
        assert category_item.timeIntervals[0].timeTo == "12:00"
        assert category_item.timeIntervals[0].quota == 25

    def test_quota_area_item_validation(self):
        """Test QuotaAreaItem model validation."""
        area_item = QuotaAreaItem(
            areaLabel="North District",
            totalQuota=200,
            usedQuota=50,
            availableQuota=150,
            categories=[
                QuotaCategoryItem(
                    categoryLabel="Maintenance",
                    totalQuota=100,
                    usedQuota=25,
                    availableQuota=75,
                )
            ],
        )

        assert area_item.areaLabel == "North District"
        assert area_item.totalQuota == 200
        assert area_item.usedQuota == 50
        assert area_item.availableQuota == 150
        assert len(area_item.categories) == 1
        assert area_item.categories[0].categoryLabel == "Maintenance"

    def test_quota_response_item_validation(self):
        """Test QuotaResponseItem model validation."""
        response_item = QuotaResponseItem(
            date="2024-01-15",
            areas=[
                QuotaAreaItem(
                    areaLabel="Central District",
                    totalQuota=250,
                    usedQuota=60,
                    availableQuota=190,
                )
            ],
        )

        assert response_item.date == "2024-01-15"
        assert len(response_item.areas) == 1
        assert response_item.areas[0].areaLabel == "Central District"
        assert response_item.areas[0].totalQuota == 250

    def test_get_quota_response_validation(self):
        """Test GetQuotaResponse model validation."""
        quota_response = GetQuotaResponse(
            items=[
                QuotaResponseItem(
                    date="2024-01-15",
                    areas=[
                        QuotaAreaItem(
                            areaLabel="District A",
                            totalQuota=500,
                            usedQuota=125,
                            availableQuota=375,
                        ),
                        QuotaAreaItem(
                            areaLabel="District B",
                            totalQuota=500,
                            usedQuota=125,
                            availableQuota=375,
                        ),
                    ],
                )
            ]
        )

        assert len(quota_response.items) == 1
        assert quota_response.items[0].date == "2024-01-15"
        # QuotaResponseItem doesn't have totalQuota field
        assert len(quota_response.items[0].areas) == 2
        assert quota_response.items[0].areas[0].areaLabel == "District A"
        assert quota_response.items[0].areas[1].areaLabel == "District B"

    def test_quota_models_inherit_base_ofs_response(self):
        """Test that quota models inherit from BaseOFSResponse."""
        models_to_test = [
            GetQuotaRequest,
            GetQuotaResponse,
            QuotaTimeInterval,
            QuotaCategoryItem,
            QuotaAreaItem,
            QuotaResponseItem,
        ]

        for model_class in models_to_test:
            assert issubclass(model_class, BaseOFSResponse), (
                f"{model_class.__name__} should inherit from BaseOFSResponse"
            )

    def test_quota_models_with_extra_fields(self):
        """Test quota models properly reject extra fields."""
        # Test that extra fields are rejected (default behavior)
        request_data = {
            "dates": ["2024-01-15"],  # Correct field name
            "areas": ["AREA1"],
            "extraField": "should be rejected",
            "anotherExtra": 123,
        }

        # This should raise a ValidationError due to extra="forbid"
        with pytest.raises(ValidationError):
            GetQuotaRequest(**request_data)

        # But without extra fields, it should work fine
        valid_data = {"dates": ["2024-01-15"], "areas": ["AREA1"]}
        request = GetQuotaRequest(**valid_data)
        assert request.dates.to_list() == ["2024-01-15"]
        assert request.areas.to_list() == ["AREA1"]

    def test_nested_quota_structure_validation(self):
        """Test complex nested quota structure validation."""
        complex_response = GetQuotaResponse(
            items=[
                QuotaResponseItem(
                    date="2024-01-15",
                    areas=[
                        QuotaAreaItem(
                            areaLabel="North Region",
                            totalQuota=500,
                            usedQuota=150,
                            availableQuota=350,
                            categories=[
                                QuotaCategoryItem(
                                    categoryLabel="Emergency Repair",
                                    workSkillLabel="Plumbing",
                                    totalQuota=100,
                                    usedQuota=30,
                                    availableQuota=70,
                                    timeIntervals=[
                                        QuotaTimeInterval(
                                            timeFrom="08:00", timeTo="12:00", quota=50
                                        ),
                                        QuotaTimeInterval(
                                            timeFrom="13:00", timeTo="17:00", quota=50
                                        ),
                                    ],
                                )
                            ],
                        )
                    ],
                )
            ]
        )

        # Validate the complex nested structure
        assert len(complex_response.items) == 1
        item = complex_response.items[0]
        assert item.date == "2024-01-15"
        assert len(item.areas) == 1

        area = item.areas[0]
        assert area.areaLabel == "North Region"
        assert len(area.categories) == 1

        category = area.categories[0]
        assert category.categoryLabel == "Emergency Repair"
        assert category.workSkillLabel == "Plumbing"
        assert len(category.timeIntervals) == 2

        # Validate time intervals
        morning_interval = category.timeIntervals[0]
        assert morning_interval.timeFrom == "08:00"
        assert morning_interval.timeTo == "12:00"
        assert morning_interval.quota == 50

        afternoon_interval = category.timeIntervals[1]
        assert afternoon_interval.timeFrom == "13:00"
        assert afternoon_interval.timeTo == "17:00"
        assert afternoon_interval.quota == 50

    def test_quota_model_serialization(self):
        """Test quota model serialization to dict."""
        request = GetQuotaRequest(
            dates=["2024-01-15"],  # Correct field name
            areas=["AREA1", "AREA2"],
            categories=["CAT1"],
        )

        request_dict = request.model_dump()
        assert "dates" in request_dict
        assert "areas" in request_dict
        assert "categories" in request_dict
        # CsvList fields serialize as {"value": "csv,string"}
        assert request_dict["dates"]["value"] == "2024-01-15"
        assert request_dict["areas"]["value"] == "AREA1,AREA2"
