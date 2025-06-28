"""Working validation tests for models that need test coverage."""

import pytest
from datetime import date

from ofsc.models.base import CsvList, Translation, TranslationList, BaseOFSResponse
from ofsc.models.capacity import GetQuotaRequest
from ofsc.models.core import GetActivityRequest, BulkUpdateRequest, BulkUpdateParameters, BulkUpdateActivityItem


class TestWorkingModelsValidation:
    """Test validation for models with correct field names and constructors."""
    
    def test_csv_list_functionality(self):
        """Test CsvList functionality with correct constructor."""
        # Test creation using from_list class method
        csv_from_list = CsvList.from_list(["item1", "item2", "item3"])
        assert csv_from_list.to_list() == ["item1", "item2", "item3"]
        assert str(csv_from_list) == "item1,item2,item3"
        
        # Test creation with value parameter
        csv_from_value = CsvList(value="area1,area2,area3")
        assert csv_from_value.to_list() == ["area1", "area2", "area3"]
        
        # Test empty list
        empty_csv = CsvList.from_list([])
        assert empty_csv.to_list() == []
        assert str(empty_csv) == ""
        
        # Test single item
        single_csv = CsvList.from_list(["single"])
        assert single_csv.to_list() == ["single"]
        assert str(single_csv) == "single"
    
    def test_translation_model_validation(self):
        """Test Translation model with correct field names."""
        # The Translation model requires 'name' field, not 'text'
        translation = Translation(
            language="en",
            name="Hello World"
        )
        
        assert translation.language == "en"
        assert translation.name == "Hello World"
        assert translation.languageISO is None
        
        # Test with optional ISO field
        translation_with_iso = Translation(
            language="es",
            name="Hola Mundo",
            languageISO="es-ES"
        )
        assert translation_with_iso.languageISO == "es-ES"
    
    def test_translation_list_validation(self):
        """Test TranslationList model."""
        translations = TranslationList([
            Translation(language="en", name="Hello"),
            Translation(language="es", name="Hola"),
            Translation(language="fr", name="Bonjour")
        ])
        
        assert len(translations.root) == 3
        assert translations.root[0].language == "en"
        assert translations.root[1].name == "Hola"
        assert translations.root[2].language == "fr"
        
        # Test iteration
        languages = [t.language for t in translations]
        assert languages == ["en", "es", "fr"]
        
        # Test mapping
        mapping = translations.map()
        assert mapping["en"].name == "Hello"
        assert mapping["es"].name == "Hola"
    
    def test_get_quota_request_validation(self):
        """Test GetQuotaRequest with correct field names."""
        # The GetQuotaRequest requires 'dates' as CsvList
        request = GetQuotaRequest(dates=["2024-01-15"])
        assert request.dates.to_list() == ["2024-01-15"]
        
        # Test with additional fields
        full_request = GetQuotaRequest(
            dates=["2024-01-15", "2024-01-16"],
            areas=["AREA1", "AREA2"],
            categories=["CAT1"],
            intervalLevel=True,
            categoryLevel=True,
            aggregateResults=False
        )
        assert full_request.dates.to_list() == ["2024-01-15", "2024-01-16"]
        assert full_request.areas.to_list() == ["AREA1", "AREA2"]
        assert full_request.categories.to_list() == ["CAT1"]
        assert full_request.intervalLevel is True
        assert full_request.categoryLevel is True
        assert full_request.aggregateResults is False
    
    def test_get_activity_request_validation(self):
        """Test GetActivityRequest with correct validation."""
        # GetActivityRequest requires resources and date range when includeNonScheduled=False
        request = GetActivityRequest(
            resources=["TECH001", "TECH002"],
            dateFrom=date(2024, 1, 15),
            dateTo=date(2024, 1, 16)
        )
        assert request.resources == ["TECH001", "TECH002"]
        assert request.dateFrom == date(2024, 1, 15)
        assert request.dateTo == date(2024, 1, 16)
        
        # Test with includeNonScheduled=True (dates not required)
        non_scheduled_request = GetActivityRequest(
            resources=["TECH001"],
            includeNonScheduled=True
        )
        assert non_scheduled_request.resources == ["TECH001"]
        assert non_scheduled_request.includeNonScheduled is True
        assert non_scheduled_request.dateFrom is None
        assert non_scheduled_request.dateTo is None
        
        # Test with optional fields
        full_request = GetActivityRequest(
            resources=["TECH001"],
            dateFrom=date(2024, 1, 15),
            dateTo=date(2024, 1, 16),
            fields=["activityId", "status"],
            limit=100,
            offset=50,
            includeChildren="all"
        )
        assert full_request.fields == ["activityId", "status"]
        assert full_request.limit == 100
        assert full_request.offset == 50
        assert full_request.includeChildren == "all"
    
    def test_bulk_update_models_validation(self):
        """Test bulk update models with correct field names."""
        # Test BulkUpdateActivityItem
        activity_item = BulkUpdateActivityItem(
            activityId=12345,
            status="started",
            resourceId="TECH001",
            customerNumber="CUST001"
        )
        assert activity_item.activityId == 12345
        assert activity_item.status == "started"
        assert activity_item.resourceId == "TECH001"
        assert activity_item.customerNumber == "CUST001"
        
        # Test BulkUpdateParameters with correct field names
        params = BulkUpdateParameters(
            identifyActivityBy="activityId",
            ifInFinalStatusThen="ignore",
            inventoryPropertiesUpdateMode="replace"
        )
        assert params.identifyActivityBy == "activityId"
        assert params.ifInFinalStatusThen == "ignore"
        assert params.inventoryPropertiesUpdateMode == "replace"
        
        # Test BulkUpdateRequest with correct field names (updateParameters, not parameters)
        request = BulkUpdateRequest(
            activities=[activity_item],
            updateParameters=params
        )
        assert len(request.activities) == 1
        assert request.activities[0].activityId == 12345
        assert request.updateParameters.identifyActivityBy == "activityId"
    
    def test_model_inheritance_and_configuration(self):
        """Test model inheritance and configuration."""
        # Test BaseOFSResponse inheritance for models that should inherit from it
        models_inheriting_base = [
            GetQuotaRequest,
            GetActivityRequest,
            BulkUpdateActivityItem,
            BulkUpdateParameters,
            BulkUpdateRequest
        ]
        
        for model_class in models_inheriting_base:
            assert issubclass(model_class, BaseOFSResponse), f"{model_class.__name__} should inherit from BaseOFSResponse"
        
        # Test that Translation inherits from BaseModel (not BaseOFSResponse)
        from pydantic import BaseModel
        assert issubclass(Translation, BaseModel)
        assert not issubclass(Translation, BaseOFSResponse)  # Translation doesn't inherit from BaseOFSResponse
    
    def test_required_field_validation(self):
        """Test required field validation with correct expectations."""
        # GetQuotaRequest requires dates
        with pytest.raises(ValueError, match="Field required"):
            GetQuotaRequest()
        
        # GetActivityRequest requires resources
        with pytest.raises(ValueError, match="Field required"):
            GetActivityRequest()
        
        # GetActivityRequest also validates date range when includeNonScheduled=False
        with pytest.raises(ValueError, match="dateFrom and dateTo are required"):
            GetActivityRequest(resources=["TECH001"])  # includeNonScheduled=False by default
        
        # BulkUpdateRequest requires activities and updateParameters
        with pytest.raises(ValueError, match="Field required"):
            BulkUpdateRequest()
        
        with pytest.raises(ValueError, match="Field required"):
            BulkUpdateRequest(activities=[])
        
        # Translation requires name
        with pytest.raises(ValueError, match="Field required"):
            Translation(language="en")  # missing name
    
    def test_models_with_extra_fields(self):
        """Test models handle extra fields according to their configuration."""
        # BulkUpdateActivityItem allows extra fields
        activity_data = {
            "activityId": 12345,
            "status": "started",
            "customField1": "value1",
            "customField2": 42,
            "extraProperty": True
        }
        
        activity_item = BulkUpdateActivityItem(**activity_data)
        assert activity_item.activityId == 12345
        assert activity_item.status == "started"
        
        # GetQuotaRequest allows extra fields  
        quota_data = {
            "dates": ["2024-01-15"],
            "areas": ["AREA1"],
            "extraField": "should be preserved"
        }
        
        quota_request = GetQuotaRequest(**quota_data)
        assert quota_request.dates.to_list() == ["2024-01-15"]
        assert quota_request.areas.to_list() == ["AREA1"]
    
    def test_model_serialization(self):
        """Test model serialization to dict."""
        # Test Translation serialization
        translation = Translation(language="en", name="Hello", languageISO="en-US")
        serialized = translation.model_dump()
        
        expected_keys = {"language", "name", "languageISO"}
        assert set(serialized.keys()) == expected_keys
        assert serialized["language"] == "en"
        assert serialized["name"] == "Hello"
        assert serialized["languageISO"] == "en-US"
        
        # Test CsvList serialization
        csv_list = CsvList.from_list(["item1", "item2"])
        csv_serialized = csv_list.model_dump()
        assert "value" in csv_serialized
        assert csv_serialized["value"] == "item1,item2"
        
        # Test complex model serialization
        request = BulkUpdateRequest(
            activities=[
                BulkUpdateActivityItem(activityId=123, status="started")
            ],
            updateParameters=BulkUpdateParameters(identifyActivityBy="activityId")
        )
        
        serialized_request = request.model_dump()
        assert "activities" in serialized_request
        assert "updateParameters" in serialized_request
        assert len(serialized_request["activities"]) == 1
        assert serialized_request["activities"][0]["activityId"] == 123
    
    def test_csv_list_edge_cases(self):
        """Test CsvList edge cases."""
        # Test empty list
        empty_csv = CsvList.from_list([])
        assert empty_csv.to_list() == []
        assert str(empty_csv) == ""
        
        # Test whitespace handling
        whitespace_csv = CsvList(value="  item1  ,  item2  ,  ")
        clean_list = whitespace_csv.to_list()
        assert clean_list == ["item1", "item2"]  # whitespace trimmed, empty items removed
        
        # Test single item
        single_csv = CsvList.from_list(["single"])
        assert single_csv.to_list() == ["single"]
        assert str(single_csv) == "single"
        
        # Test CSV parsing
        csv_string = CsvList(value="a,b,c,d")
        assert csv_string.to_list() == ["a", "b", "c", "d"]
    
    def test_complex_nested_scenarios(self):
        """Test complex nested validation scenarios."""
        # Create complex bulk update with multiple activities
        complex_request = BulkUpdateRequest(
            activities=[
                BulkUpdateActivityItem(
                    activityId=1001,
                    activityType="Installation",
                    status="started",
                    resourceId="TECH001",
                    date="2024-01-15"
                ),
                BulkUpdateActivityItem(
                    activityId=1002,
                    activityType="Maintenance",
                    status="completed",
                    resourceId="TECH002",
                    customerId="CUST002"
                )
            ],
            updateParameters=BulkUpdateParameters(
                identifyActivityBy="activityId",
                ifInFinalStatusThen="update",
                fallbackResource="SUPERVISOR",
                inventoryPropertiesUpdateMode="merge"
            )
        )
        
        # Validate the nested structure
        assert len(complex_request.activities) == 2
        
        # First activity
        activity1 = complex_request.activities[0]
        assert activity1.activityId == 1001
        assert activity1.activityType == "Installation"
        assert activity1.status == "started"
        assert activity1.resourceId == "TECH001"
        assert activity1.date == "2024-01-15"
        
        # Second activity
        activity2 = complex_request.activities[1]
        assert activity2.activityId == 1002
        assert activity2.activityType == "Maintenance"
        assert activity2.status == "completed"
        assert activity2.resourceId == "TECH002"
        assert activity2.customerId == "CUST002"
        
        # Update parameters
        params = complex_request.updateParameters
        assert params.identifyActivityBy == "activityId"
        assert params.ifInFinalStatusThen == "update"
        assert params.fallbackResource == "SUPERVISOR"
        assert params.inventoryPropertiesUpdateMode == "merge"
    
    def test_translation_list_utilities(self):
        """Test TranslationList mapping and iteration utilities."""
        translations = TranslationList([
            Translation(language="en", name="English Text"),
            Translation(language="es", name="Texto Español", languageISO="es-ES"),
            Translation(language="fr", name="Texte Français", languageISO="fr-FR")
        ])
        
        # Test length
        assert len(translations.root) == 3
        
        # Test iteration
        for i, translation in enumerate(translations):
            assert isinstance(translation, Translation)
            if i == 0:
                assert translation.language == "en"
                assert translation.name == "English Text"
        
        # Test indexing
        assert translations[0].language == "en"
        assert translations[1].languageISO == "es-ES"
        assert translations[2].name == "Texte Français"
        
        # Test mapping functionality
        lang_map = translations.map()
        assert "en" in lang_map
        assert "es" in lang_map
        assert "fr" in lang_map
        assert lang_map["en"].name == "English Text"
        assert lang_map["es"].languageISO == "es-ES"
        assert lang_map["fr"].name == "Texte Français"