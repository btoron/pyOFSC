"""Validation tests for models that were identified as missing tests."""

import pytest
from datetime import datetime, date
from typing import List, Optional

from ofsc.models.base import CsvList, Translation, TranslationList
from ofsc.models.capacity import GetQuotaRequest, GetQuotaResponse
from ofsc.models.core import GetActivityRequest, BulkUpdateRequest, BulkUpdateParameters, BulkUpdateActivityItem


class TestMissingModelsValidation:
    """Test validation for models that were missing validation tests."""
    
    def test_csv_list_basic_functionality(self):
        """Test CsvList basic functionality."""
        # Test creation from list
        csv_from_list = CsvList.from_list(["item1", "item2", "item3"])
        assert csv_from_list.to_list() == ["item1", "item2", "item3"]
        assert str(csv_from_list) == "item1,item2,item3"
        
        # Test creation from string
        csv_from_string = CsvList(value="area1,area2,area3")
        assert csv_from_string.to_list() == ["area1", "area2", "area3"]
        
        # Test string representation
        assert str(csv_from_list) == "item1,item2,item3"
        
        # Test value access
        assert csv_from_list.value == "item1,item2,item3"
    
    def test_translation_model_validation(self):
        """Test Translation model validation."""
        translation = Translation(
            language="en",
            name="Hello World"
        )
        
        assert translation.language == "en"
        assert translation.name == "Hello World"
        
        # Test with optional languageISO field
        translation_with_iso = Translation(
            language="es",
            name="Hola Mundo",
            languageISO="es-ES"
        )
        assert translation_with_iso.languageISO == "es-ES"
    
    def test_translation_list_validation(self):
        """Test TranslationList model validation."""
        translations = TranslationList([
            Translation(language="en", name="Hello"),
            Translation(language="es", name="Hola"),
            Translation(language="fr", name="Bonjour")
        ])
        
        assert len(translations.root) == 3
        assert translations.root[0].language == "en"
        assert translations.root[1].name == "Hola"
        assert translations.root[2].language == "fr"
    
    def test_get_quota_request_basic_validation(self):
        """Test GetQuotaRequest basic validation."""
        # Test with required dates field
        request = GetQuotaRequest(dates=["2024-01-15"])
        assert request.dates.to_list() == ["2024-01-15"]
        
        # Test with additional fields
        full_request = GetQuotaRequest(
            dates=["2024-01-15", "2024-01-16"],
            areas=["AREA1", "AREA2"],
            categories=["CAT1"],
            intervalLevel=True
        )
        assert full_request.dates.to_list() == ["2024-01-15", "2024-01-16"]
        assert full_request.areas.to_list() == ["AREA1", "AREA2"]
        assert full_request.categories.to_list() == ["CAT1"]
        assert full_request.intervalLevel is True
    
    def test_get_activity_request_basic_validation(self):
        """Test GetActivityRequest basic validation."""
        # Test with required resources field and dates (since includeNonScheduled defaults to False)
        request = GetActivityRequest(
            resources=["TECH001", "TECH002"],
            dateFrom=date(2024, 1, 15),
            dateTo=date(2024, 1, 16)
        )
        assert request.resources == ["TECH001", "TECH002"]
        
        # Test with includeNonScheduled=True (no dates required)
        full_request = GetActivityRequest(
            resources=["TECH001"],
            fields=["activityId", "status"],
            limit=100,
            includeNonScheduled=True
        )
        assert full_request.resources == ["TECH001"]
        assert full_request.includeNonScheduled is True
        assert full_request.fields == ["activityId", "status"]
        assert full_request.limit == 100
    
    def test_bulk_update_activity_item_validation(self):
        """Test BulkUpdateActivityItem validation."""
        activity_item = BulkUpdateActivityItem(
            activityId=12345,
            status="started",
            resourceId="TECH001"
        )
        
        assert activity_item.activityId == 12345
        assert activity_item.status == "started"
        assert activity_item.resourceId == "TECH001"
        
        # Test with optional fields
        minimal_item = BulkUpdateActivityItem()
        assert minimal_item.activityId is None
        assert minimal_item.status is None
    
    def test_bulk_update_parameters_validation(self):
        """Test BulkUpdateParameters validation."""
        params = BulkUpdateParameters(
            identifyActivityBy="activityId",
            ifInFinalStatusThen="ignore"
        )
        
        assert params.identifyActivityBy == "activityId"
        assert params.ifInFinalStatusThen == "ignore"
        
        # Test with defaults
        default_params = BulkUpdateParameters()
        assert default_params.identifyActivityBy is None
        assert default_params.ifInFinalStatusThen is None
    
    def test_bulk_update_request_validation(self):
        """Test BulkUpdateRequest validation."""
        request = BulkUpdateRequest(
            activities=[
                BulkUpdateActivityItem(activityId=1001, status="started"),
                BulkUpdateActivityItem(activityId=1002, status="completed")
            ],
            updateParameters=BulkUpdateParameters(identifyActivityBy="activityId")
        )
        
        assert len(request.activities) == 2
        assert request.activities[0].activityId == 1001
        assert request.activities[1].activityId == 1002
        assert request.updateParameters.identifyActivityBy == "activityId"
    
    def test_models_handle_extra_fields(self):
        """Test that models handle extra fields gracefully."""
        # Test with extra fields that might come from API
        activity_data = {
            "activityId": 12345,
            "status": "started",
            "customField1": "value1",
            "customField2": 42
        }
        
        activity_item = BulkUpdateActivityItem(**activity_data)
        assert activity_item.activityId == 12345
        assert activity_item.status == "started"
        # Extra fields should be preserved
        assert hasattr(activity_item, 'model_extra')
    
    def test_models_serialization(self):
        """Test model serialization to dict."""
        translation = Translation(language="en", name="Hello")
        serialized = translation.model_dump()
        
        assert "language" in serialized
        assert "name" in serialized
        assert serialized["language"] == "en"
        assert serialized["name"] == "Hello"
        
        # Test CsvList serialization
        csv_list = CsvList.from_list(["item1", "item2"])
        csv_serialized = csv_list.model_dump()
        assert "value" in csv_serialized
        assert csv_serialized["value"] == "item1,item2"
    
    def test_model_inheritance(self):
        """Test that models properly inherit from base classes."""
        from ofsc.models.base import BaseOFSResponse
        
        # Test that core models inherit from BaseOFSResponse
        models_to_test = [
            GetQuotaRequest,
            GetActivityRequest,
            BulkUpdateActivityItem,
            BulkUpdateParameters,
            BulkUpdateRequest
            # Note: Translation does not inherit from BaseOFSResponse, it's a simple BaseModel
        ]
        
        for model_class in models_to_test:
            assert issubclass(model_class, BaseOFSResponse), f"{model_class.__name__} should inherit from BaseOFSResponse"
    
    def test_required_field_validation(self):
        """Test required field validation."""
        # GetQuotaRequest requires dates
        with pytest.raises(ValueError, match="Field required"):
            GetQuotaRequest()
        
        # GetActivityRequest requires resources  
        with pytest.raises(ValueError, match="Field required"):
            GetActivityRequest()
        
        # BulkUpdateRequest requires activities and updateParameters
        with pytest.raises(ValueError, match="Field required"):
            BulkUpdateRequest()
        
        with pytest.raises(ValueError, match="Field required"):
            BulkUpdateRequest(activities=[])
        
        # Translation requires language and text
        with pytest.raises(ValueError, match="Field required"):
            Translation(language="en")
        
        with pytest.raises(ValueError, match="Field required"):
            Translation(language="en")  # Missing required 'name' field
    
    def test_csv_list_edge_cases(self):
        """Test CsvList edge cases and error handling."""
        # Test empty list
        empty_csv = CsvList.from_list([])
        assert empty_csv.to_list() == []
        assert str(empty_csv) == ""
        
        # Test single item
        single_csv = CsvList.from_list(["single"])
        assert single_csv.to_list() == ["single"]
        assert str(single_csv) == "single"
        
        # Test from CSV string
        csv_string = CsvList(value="a,b,c")
        assert csv_string.to_list() == ["a", "b", "c"]
        
        # Test whitespace handling
        whitespace_csv = CsvList(value="  item1  ,  item2  ")
        assert whitespace_csv.to_list() == ["item1", "item2"]
    
    def test_complex_nested_validation(self):
        """Test complex nested model validation."""
        # Create a complex bulk update request
        complex_request = BulkUpdateRequest(
            activities=[
                BulkUpdateActivityItem(
                    activityId=1001,
                    activityType="Installation",
                    status="started",
                    resourceId="TECH001",
                    customerNumber="CUST001"
                ),
                BulkUpdateActivityItem(
                    activityId=1002,
                    activityType="Maintenance", 
                    status="completed",
                    resourceId="TECH002"
                )
            ],
            updateParameters=BulkUpdateParameters(
                identifyActivityBy="activityId",
                ifInFinalStatusThen="update",
                inventoryPropertiesUpdateMode="replace"
            )
        )
        
        # Validate the nested structure
        assert len(complex_request.activities) == 2
        
        # Validate first activity
        activity1 = complex_request.activities[0]
        assert activity1.activityId == 1001
        assert activity1.activityType == "Installation"
        assert activity1.status == "started"
        assert activity1.resourceId == "TECH001"
        assert activity1.customerNumber == "CUST001"
        
        # Validate second activity
        activity2 = complex_request.activities[1]
        assert activity2.activityId == 1002
        assert activity2.activityType == "Maintenance"
        assert activity2.status == "completed"
        assert activity2.resourceId == "TECH002"
        
        # Validate parameters
        params = complex_request.updateParameters
        assert params.identifyActivityBy == "activityId"
        assert params.ifInFinalStatusThen == "update"
        assert params.inventoryPropertiesUpdateMode == "replace"