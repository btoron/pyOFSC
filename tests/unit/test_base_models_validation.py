"""Validation tests for base models in OFSC v3.0."""

import pytest
from typing import List, Optional, Any, Dict
from pydantic import ValidationError

from ofsc.models.base import (
    CsvList,
    BaseOFSResponse,
    OFSResponseList,
    SharingEnum,
    EntityEnum,
    Translation,
    TranslationList
)


class TestBaseModelsValidation:
    """Test validation for base infrastructure models."""
    
    def test_csv_list_validation(self):
        """Test CsvList model validation and conversion."""
        # Test creation from list
        csv_list = CsvList.from_list(["item1", "item2", "item3"])
        assert csv_list.value == "item1,item2,item3"
        
        # Test creation from value string
        csv_string = CsvList(value="item1,item2,item3")
        assert csv_string.value == "item1,item2,item3"
        
        # Test creation from single item
        single_item = CsvList(value="single_item")
        assert single_item.value == "single_item"
        
        # Test empty list
        empty_list = CsvList.from_list([])
        assert empty_list.value == ""
        
        # Test empty string
        empty_string = CsvList(value="")
        assert empty_string.value == ""
    
    def test_csv_list_conversion_methods(self):
        """Test CsvList conversion methods."""
        csv_list = CsvList.from_list(["area1", "area2", "area3"])
        
        # Test to_list method (CsvList doesn't have to_string, the value IS the string)
        assert csv_list.to_list() == ["area1", "area2", "area3"]
        
        # Test string representation
        assert str(csv_list) == "area1,area2,area3"
        
        # Test empty value to_list
        empty_csv = CsvList(value="")
        assert empty_csv.to_list() == []
    
    def test_csv_list_edge_cases(self):
        """Test CsvList edge cases and error handling."""
        # Test with empty string
        empty_list = CsvList(value="")
        assert empty_list.to_list() == []
        
        # Test with whitespace in string
        whitespace_string = CsvList(value="  item1  ,  item2  ,  item3  ")
        assert whitespace_string.to_list() == ["item1", "item2", "item3"]
        
        # Test with single item
        single = CsvList(value="single")
        assert single.to_list() == ["single"]
        
        # Test with spaces only
        spaces = CsvList(value="   ")
        assert spaces.to_list() == []
    
    def test_csv_list_capacity_integration(self):
        """Test CsvList integration with capacity model fields."""
        # Test typical capacity usage patterns
        areas_csv = CsvList.from_list(["North", "South", "East", "West"])
        assert areas_csv.value == "North,South,East,West"
        
        categories_csv = CsvList(value="Installation,Maintenance,Repair")
        assert categories_csv.to_list() == ["Installation", "Maintenance", "Repair"]
        
        # Test single area
        single_area = CsvList(value="Central")
        assert single_area.value == "Central"
        assert single_area.to_list() == ["Central"]
    
    def test_translation_validation(self):
        """Test Translation model validation."""
        translation = Translation(
            language="en",
            name="Hello World"
        )
        
        assert translation.language == "en"
        assert translation.name == "Hello World"
        
        # Test with optional fields
        full_translation = Translation(
            language="es",
            name="Hola Mundo",
            languageISO="es-ES"
        )
        
        assert full_translation.language == "es"
        assert full_translation.name == "Hola Mundo"
        assert full_translation.languageISO == "es-ES"
    
    def test_translation_required_fields(self):
        """Test Translation required field validation."""
        # Language has default value "en", so only name is required
        # Missing name should raise validation error
        with pytest.raises(ValidationError, match="Field required"):
            Translation(language="en")
    
    def test_translation_list_validation(self):
        """Test TranslationList model validation."""
        translations = TranslationList([
            Translation(language="en", name="Hello"),
            Translation(language="es", name="Hola"),
            Translation(language="fr", name="Bonjour")
        ])
        
        assert len(translations.root) == 3
        assert translations.root[0].language == "en"
        assert translations.root[0].name == "Hello"
        assert translations.root[1].language == "es"
        assert translations.root[1].name == "Hola"
        assert translations.root[2].language == "fr"
        assert translations.root[2].name == "Bonjour"
    
    def test_translation_list_empty(self):
        """Test TranslationList with empty list."""
        empty_translations = TranslationList([])
        assert len(empty_translations.root) == 0
        assert list(empty_translations.root) == []
    
    def test_translation_list_iteration(self):
        """Test TranslationList iteration and access methods."""
        translations = TranslationList([
            Translation(language="en", name="Yes"),
            Translation(language="es", name="Sí")
        ])
        
        # Test iteration
        languages = [t.language for t in translations]
        assert languages == ["en", "es"]
        
        # Test indexing
        assert translations[0].language == "en"
        assert translations[1].name == "Sí"
    
    def test_sharing_enum_values(self):
        """Test SharingEnum contains expected values."""
        # Test that the enum contains the documented values
        expected_values = {"area", "category", "maximal", "no sharing", "private", "summary"}
        actual_values = {e.value for e in SharingEnum}
        
        # Check that all expected values are present
        assert actual_values == expected_values
        
        # Test enum usage
        assert SharingEnum.area == "area"
        assert SharingEnum.category == "category"
        assert SharingEnum.no_sharing == "no sharing"
        assert SharingEnum.maximal == "maximal"
        assert SharingEnum.private == "private"
        assert SharingEnum.summary == "summary"
    
    def test_entity_enum_values(self):
        """Test EntityEnum contains expected values."""
        # Test basic entity types
        expected_entities = {"activity", "inventory", "resource", "service request", "user"}
        actual_values = {e.value for e in EntityEnum}
        
        # Check that all expected values are present
        assert actual_values == expected_entities
    
    def test_base_ofs_response_inheritance(self):
        """Test BaseOFSResponse inheritance and functionality."""
        # Create a simple test model that inherits from BaseOFSResponse
        class TestModel(BaseOFSResponse):
            name: str
            value: int
        
        # Test creation
        test_model = TestModel(name="test", value=42)
        assert test_model.name == "test"
        assert test_model.value == 42
        
        # Test that it has BaseOFSResponse attributes
        assert hasattr(test_model, '_raw_response')
        assert hasattr(test_model, 'from_response')
    
    def test_ofs_response_list_validation(self):
        """Test OFSResponseList generic validation."""
        # Create a simple test model for the list
        class TestItem(BaseOFSResponse):
            id: int
            name: str
        
        # Create a response list
        test_items = [
            TestItem(id=1, name="Item 1"),
            TestItem(id=2, name="Item 2"),
            TestItem(id=3, name="Item 3")
        ]
        
        response_list = OFSResponseList[TestItem](items=test_items)
        
        assert len(response_list.items) == 3
        assert response_list.items[0].id == 1
        assert response_list.items[0].name == "Item 1"
        assert response_list.items[2].id == 3
        assert response_list.items[2].name == "Item 3"
    
    def test_ofs_response_list_empty(self):
        """Test OFSResponseList with empty list."""
        class TestItem(BaseOFSResponse):
            value: str
        
        empty_list = OFSResponseList[TestItem](items=[])
        assert len(empty_list.items) == 0
        assert list(empty_list.items) == []
    
    def test_base_models_extra_fields_handling(self):
        """Test that base models handle extra fields appropriately."""
        # Test Translation with extra fields
        translation_data = {
            "language": "en",
            "name": "Hello",
            "extraField": "should be preserved",
            "numericExtra": 123
        }
        
        translation = Translation(**translation_data)
        assert translation.language == "en"
        assert translation.name == "Hello"
        # Translation model doesn't preserve extra fields by default
    
    def test_csv_list_serialization(self):
        """Test CsvList serialization and deserialization."""
        original_list = CsvList.from_list(["area1", "area2", "area3"])
        
        # Test model_dump
        serialized = original_list.model_dump()
        assert "value" in serialized
        assert serialized["value"] == "area1,area2,area3"
        
        # Test round-trip serialization
        recreated = CsvList(**serialized)
        assert recreated.value == original_list.value
        assert str(recreated) == str(original_list)
    
    def test_translation_serialization(self):
        """Test Translation serialization."""
        translation = Translation(
            language="fr",
            name="Bonjour le monde",
            languageISO="fr-FR"
        )
        
        serialized = translation.model_dump()
        assert serialized["language"] == "fr"
        assert serialized["name"] == "Bonjour le monde"
        assert serialized["languageISO"] == "fr-FR"
    
    def test_base_models_type_validation(self):
        """Test type validation in base models."""
        # Test CsvList type validation
        with pytest.raises(ValidationError):
            CsvList(value=123)  # Should not accept plain numbers for value
        
        # Test Translation type validation
        with pytest.raises(ValidationError):
            Translation(language=123, name="Hello")  # language should be string
        
        with pytest.raises(ValidationError):
            Translation(language="en", name=123)  # name should be string
    
    def test_csv_list_performance_with_large_data(self):
        """Test CsvList performance with larger datasets."""
        # Test with a larger list (simulating real-world usage)
        large_list = [f"area_{i}" for i in range(100)]
        csv_large = CsvList.from_list(large_list)
        
        assert len(csv_large.to_list()) == 100
        assert csv_large.to_list()[0] == "area_0"
        assert csv_large.to_list()[99] == "area_99"
        
        # Test string conversion performance
        csv_string = csv_large.value
        assert csv_string.startswith("area_0,area_1")
        assert csv_string.endswith("area_98,area_99")
        
        # Test that conversion back works
        recreated = CsvList(value=csv_string)
        assert recreated.to_list() == csv_large.to_list()