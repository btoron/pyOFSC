"""Validation tests for bulk operation models in OFSC v3.0."""

import pytest
from datetime import datetime, date
from typing import List, Optional, Dict, Any

from ofsc.models.core import (
    GetActivityRequest,
    BulkUpdateActivityItem,
    BulkUpdateParameters,
    BulkUpdateRequest,
    BulkUpdateError,
    BulkUpdateWarning,
    BulkUpdateResult,
    BulkUpdateResponse,
    ActivityKeys
)
from ofsc.models.base import BaseOFSResponse


class TestBulkOperationModelsValidation:
    """Test validation for bulk operation models."""
    
    def test_get_activity_request_validation(self):
        """Test GetActivityRequest model validation."""
        from datetime import date
        
        # Test minimal request (resources and dates are required when includeNonScheduled=False)
        request = GetActivityRequest(
            resources=["TECH001"],
            dateFrom=date(2024, 1, 1),
            dateTo=date(2024, 1, 31)
        )
        
        assert request.resources == ["TECH001"]
        assert request.fields is None
        assert request.includeChildren == "all"
        
        # Test with includeNonScheduled=True (no dates required)
        full_request = GetActivityRequest(
            resources=["TECH001", "TECH002"],
            fields=["activityId", "activityType", "status"],
            includeNonScheduled=True
        )
        
        assert full_request.resources == ["TECH001", "TECH002"]
        assert full_request.fields == ["activityId", "activityType", "status"]
        assert full_request.includeNonScheduled is True
    
    def test_get_activity_request_required_fields(self):
        """Test GetActivityRequest required field validation."""
        # Missing resources should raise validation error
        with pytest.raises(ValueError, match="Field required"):
            GetActivityRequest()
    
    def test_activity_keys_validation(self):
        """Test ActivityKeys model validation."""
        keys = ActivityKeys(
            activityId=12345,
            apptNumber="APPT001",
            customerNumber="CUST001"
        )
        
        assert keys.activityId == 12345
        assert keys.apptNumber == "APPT001"
        assert keys.customerNumber == "CUST001"
        
        # Test with optional fields
        keys_optional = ActivityKeys()
        assert keys_optional.activityId is None
        assert keys_optional.apptNumber is None
        assert keys_optional.customerNumber is None
    
    def test_bulk_update_activity_item_validation(self):
        """Test BulkUpdateActivityItem model validation."""
        activity_item = BulkUpdateActivityItem(
            activityId=12345,
            status="started",
            teamTravelTime=30,
            customerNumber="CUST001"
        )
        
        assert activity_item.activityId == 12345
        assert activity_item.status == "started"
        assert activity_item.teamTravelTime == 30
        assert activity_item.customerNumber == "CUST001"
    
    def test_bulk_update_activity_item_with_extra_fields(self):
        """Test BulkUpdateActivityItem with dynamic fields."""
        # Test with custom fields that might be added dynamically
        activity_data = {
            "activityId": 12345,
            "status": "started",
            "customField1": "value1",
            "customField2": 42,
            "customField3": True
        }
        
        activity_item = BulkUpdateActivityItem(**activity_data)
        assert activity_item.activityId == 12345
        assert activity_item.status == "started"
        # Custom fields should be accessible through model_extra
        assert hasattr(activity_item, 'model_extra')
    
    def test_bulk_update_parameters_validation(self):
        """Test BulkUpdateParameters model validation."""
        params = BulkUpdateParameters(
            identifyActivityBy="activityId",
            fallbackResource="TECH999",
            ifInFinalStatusThen="ignore"
        )
        
        assert params.identifyActivityBy == "activityId"
        assert params.fallbackResource == "TECH999"
        assert params.ifInFinalStatusThen == "ignore"
        
        # Test with defaults
        default_params = BulkUpdateParameters()
        assert default_params.identifyActivityBy is None
        assert default_params.fallbackResource is None
        assert default_params.ifInFinalStatusThen is None
    
    def test_bulk_update_request_validation(self):
        """Test BulkUpdateRequest model validation."""
        request = BulkUpdateRequest(
            activities=[
                BulkUpdateActivityItem(
                    activityId=12345,
                    status="started"
                ),
                BulkUpdateActivityItem(
                    activityId=67890,
                    status="completed"
                )
            ],
            updateParameters=BulkUpdateParameters(
                identifyActivityBy="activityId",
                fallbackResource="TECH999"
            )
        )
        
        assert len(request.activities) == 2
        assert request.activities[0].activityId == 12345
        assert request.activities[0].status == "started"
        assert request.activities[1].activityId == 67890
        assert request.activities[1].status == "completed"
        assert request.updateParameters.identifyActivityBy == "activityId"
        assert request.updateParameters.fallbackResource == "TECH999"
    
    def test_bulk_update_request_required_fields(self):
        """Test BulkUpdateRequest required field validation."""
        # Missing activities should raise validation error
        with pytest.raises(ValueError, match="Field required"):
            BulkUpdateRequest(updateParameters=BulkUpdateParameters())
        
        # Empty activities list should be valid (if updateParameters is provided)
        request = BulkUpdateRequest(activities=[], updateParameters=BulkUpdateParameters())
        assert request.activities == []
        assert request.updateParameters is not None
    
    def test_bulk_update_error_validation(self):
        """Test BulkUpdateError model validation."""
        error = BulkUpdateError(
            errorDetail="Invalid status transition",
            operation="update_status"
        )
        
        assert error.errorDetail == "Invalid status transition"
        assert error.operation == "update_status"
        
        # Test with defaults
        default_error = BulkUpdateError()
        assert default_error.errorDetail is None
        assert default_error.operation is None
    
    def test_bulk_update_warning_validation(self):
        """Test BulkUpdateWarning model validation."""
        warning = BulkUpdateWarning(
            code=101,
            message=200  # message is an integer according to the model
        )
        
        assert warning.code == 101
        assert warning.message == 200
        
        # Test with defaults
        default_warning = BulkUpdateWarning()
        assert default_warning.code is None
        assert default_warning.message is None
    
    def test_bulk_update_result_validation(self):
        """Test BulkUpdateResult model validation."""
        result = BulkUpdateResult(
            activityKeys=ActivityKeys(
                activityId=11111,
                apptNumber="APPT123"
            ),
            errors=[
                BulkUpdateError(errorDetail="Some error", operation="update")
            ],
            warnings=[
                BulkUpdateWarning(code=200, message=300)
            ]
        )
        
        assert result.activityKeys.activityId == 11111
        assert result.activityKeys.apptNumber == "APPT123"
        assert len(result.errors) == 1
        assert result.errors[0].errorDetail == "Some error"
        assert len(result.warnings) == 1
        assert result.warnings[0].message == 300
    
    def test_bulk_update_response_validation(self):
        """Test BulkUpdateResponse model validation."""
        response = BulkUpdateResponse(
            results=[
                BulkUpdateResult(
                    activityKeys=ActivityKeys(activityId=12345),
                    errors=[
                        BulkUpdateError(errorDetail="Some error", operation="update")
                    ],
                    warnings=[
                        BulkUpdateWarning(code=200, message=300)
                    ]
                ),
                BulkUpdateResult(
                    activityKeys=ActivityKeys(activityId=67890),
                    errors=[],
                    warnings=[]
                )
            ]
        )
        
        assert len(response.results) == 2
        
        # Validate nested structures
        assert response.results[0].activityKeys.activityId == 12345
        assert len(response.results[0].errors) == 1
        assert response.results[0].errors[0].errorDetail == "Some error"
        
        assert response.results[1].activityKeys.activityId == 67890
        assert len(response.results[1].errors) == 0
    
    def test_bulk_operation_models_inherit_base_ofs_response(self):
        """Test that bulk operation models inherit from BaseOFSResponse."""
        models_to_test = [
            GetActivityRequest,
            BulkUpdateActivityItem,
            BulkUpdateParameters,
            BulkUpdateRequest,
            ActivityKeys,
            BulkUpdateError,
            BulkUpdateWarning,
            BulkUpdateResult,
            BulkUpdateResponse
        ]
        
        for model_class in models_to_test:
            assert issubclass(model_class, BaseOFSResponse), f"{model_class.__name__} should inherit from BaseOFSResponse"
    
    def test_complex_bulk_update_scenario(self):
        """Test a complex bulk update scenario with multiple types of results."""
        complex_request = BulkUpdateRequest(
            activities=[
                BulkUpdateActivityItem(
                    activityId=1001,
                    status="started",
                    timeSlot="09:00-11:00"
                ),
                BulkUpdateActivityItem(
                    activityId=1002,
                    status="completed",
                    actualEndTime="2024-01-15T16:30:00Z"
                ),
                BulkUpdateActivityItem(
                    activityId=1003,
                    status="cancelled",
                    cancelReason="Customer unavailable"
                )
            ],
            updateParameters=BulkUpdateParameters(
                identifyActivityBy="activityId",
                fallbackResource="FALLBACK",
                ifInFinalStatusThen="update"
            )
        )
        
        # Validate the complex request structure
        assert len(complex_request.activities) == 3
        assert complex_request.activities[0].activityId == 1001
        assert complex_request.activities[0].status == "started"
        assert complex_request.updateParameters.identifyActivityBy == "activityId"
        assert complex_request.activities[1].activityId == 1002
        assert complex_request.activities[1].status == "completed"
        assert complex_request.activities[2].activityId == 1003
        assert complex_request.activities[2].status == "cancelled"
        
        # All validations completed above
    
    def test_bulk_operation_model_serialization(self):
        """Test bulk operation model serialization to dict."""
        request = BulkUpdateRequest(
            activities=[
                BulkUpdateActivityItem(
                    activityId=12345,
                    status="started"
                )
            ],
            updateParameters=BulkUpdateParameters(
                identifyActivityBy="activityId"
            )
        )
        
        request_dict = request.model_dump()
        assert "activities" in request_dict
        assert "updateParameters" in request_dict
        assert len(request_dict["activities"]) == 1
        assert request_dict["activities"][0]["activityId"] == 12345
        assert request_dict["activities"][0]["status"] == "started"
        assert request_dict["updateParameters"]["identifyActivityBy"] == "activityId"
    
    def test_bulk_update_with_none_values(self):
        """Test bulk update models handle None values properly."""
        # Test that None values are handled correctly
        activity_item = BulkUpdateActivityItem(
            activityId=12345,
            status=None,  # Explicitly set to None
            teamTravelTime=None
        )
        
        assert activity_item.activityId == 12345
        assert activity_item.status is None
        assert activity_item.teamTravelTime is None
        
        # Test serialization with None values
        serialized = activity_item.model_dump()
        assert serialized["activityId"] == 12345
        # None values should be included in serialization
        assert "status" in serialized
        assert serialized["status"] is None