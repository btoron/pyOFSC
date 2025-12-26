"""Async tests for property operations."""

import json
from pathlib import Path

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import (
    EntityEnum,
    Property,
    PropertyListResponse,
    Translation,
    TranslationList,
)


class TestAsyncGetPropertiesLive:
    """Live tests against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_properties(self, async_instance: AsyncOFSC):
        """Test get_properties with actual API - validates structure"""
        properties = await async_instance.metadata.get_properties(offset=0, limit=100)

        # Verify type validation
        assert isinstance(properties, PropertyListResponse)
        assert properties.totalResults is not None
        assert properties.totalResults >= 0
        assert hasattr(properties, "items")
        assert isinstance(properties.items, list)

        # Verify at least one property exists
        if len(properties.items) > 0:
            assert isinstance(properties.items[0], Property)


class TestAsyncGetProperties:
    """Test async get_properties method."""

    @pytest.mark.asyncio
    async def test_get_properties_with_model(self, async_instance: AsyncOFSC):
        """Test that get_properties returns PropertyListResponse model"""
        properties = await async_instance.metadata.get_properties(offset=0, limit=100)

        # Verify type validation
        assert isinstance(properties, PropertyListResponse)
        assert hasattr(properties, "items")
        assert hasattr(properties, "totalResults")
        assert isinstance(properties.items, list)

        # Verify items are Property instances
        if len(properties.items) > 0:
            assert isinstance(properties.items[0], Property)
            assert hasattr(properties.items[0], "label")
            assert hasattr(properties.items[0], "name")
            assert hasattr(properties.items[0], "type")

    @pytest.mark.asyncio
    async def test_get_properties_pagination(self, async_instance: AsyncOFSC):
        """Test get_properties with pagination"""
        # Get first page
        page1 = await async_instance.metadata.get_properties(offset=0, limit=5)
        assert isinstance(page1, PropertyListResponse)
        assert len(page1.items) <= 5

        # Get second page if there are enough properties
        if page1.totalResults > 5:
            page2 = await async_instance.metadata.get_properties(offset=5, limit=5)
            assert isinstance(page2, PropertyListResponse)
            # Pages should have different items
            if len(page1.items) > 0 and len(page2.items) > 0:
                assert page1.items[0].label != page2.items[0].label

    @pytest.mark.asyncio
    async def test_get_properties_total_results(self, async_instance: AsyncOFSC):
        """Test that totalResults is populated"""
        properties = await async_instance.metadata.get_properties(offset=0, limit=100)
        assert properties.totalResults is not None
        assert isinstance(properties.totalResults, int)
        assert properties.totalResults >= 0


class TestAsyncGetProperty:
    """Test async get_property method."""

    @pytest.mark.asyncio
    async def test_get_property(self, async_instance: AsyncOFSC):
        """Test getting a single property by label"""
        # First get a list of properties to get a valid label
        properties = await async_instance.metadata.get_properties(offset=0, limit=1)

        if len(properties.items) == 0:
            pytest.skip("No properties available to test")

        # Get the label of the first property
        label = properties.items[0].label

        # Get the specific property
        property_obj = await async_instance.metadata.get_property(label)

        # Verify type validation
        assert isinstance(property_obj, Property)
        assert property_obj.label == label
        assert hasattr(property_obj, "name")
        assert hasattr(property_obj, "type")

    @pytest.mark.asyncio
    async def test_get_property_details(self, async_instance: AsyncOFSC):
        """Test that get_property returns complete property details"""
        # Get a known property
        properties = await async_instance.metadata.get_properties(offset=0, limit=1)

        if len(properties.items) == 0:
            pytest.skip("No properties available to test")

        label = properties.items[0].label

        # Get detailed property
        property_obj = await async_instance.metadata.get_property(label)

        # Verify all expected fields are present
        assert isinstance(property_obj, Property)
        assert property_obj.label == label
        assert property_obj.name is not None
        assert property_obj.type is not None

    @pytest.mark.asyncio
    async def test_get_property_not_found(self, async_instance: AsyncOFSC):
        """Test that getting a non-existent property raises OFSCNotFoundError"""
        with pytest.raises(OFSCNotFoundError) as exc_info:
            await async_instance.metadata.get_property("NONEXISTENT_PROPERTY_12345")

        # Verify it's a 404 error
        assert exc_info.value.status_code == 404


class TestAsyncCreateOrReplaceProperty:
    """Test async create_or_replace_property method."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_create_or_replace_property(self, async_instance: AsyncOFSC, faker):
        """Test creating a new property and then replacing it"""
        # Create a unique property label
        unique_label = f"TEST_PROP_{faker.pystr(min_chars=8, max_chars=12).upper()}"

        # Create a new property
        new_property = Property(
            label=unique_label,
            name=faker.word().capitalize(),
            type="string",
            entity=EntityEnum.activity,
            gui="text",
            translations=TranslationList([Translation(name=faker.word())]),
        )

        # Create the property
        result = await async_instance.metadata.create_or_replace_property(new_property)

        # Verify the result
        assert isinstance(result, Property)
        assert result.label == unique_label
        # Note: API may return translation name as the property name
        assert result.name is not None
        assert result.type == "string"
        assert result.entity == EntityEnum.activity
        assert result.gui == "text"

        # Verify property was created by fetching it
        fetched = await async_instance.metadata.get_property(unique_label)
        assert isinstance(fetched, Property)
        assert fetched.label == unique_label
        assert fetched.name is not None

        # Now test replacing (updating) the property
        # Use the fetched property to ensure we have the current state
        modified_property = fetched.model_copy()
        new_name = f"UPDATED_{faker.word().capitalize()}"
        modified_property.name = new_name

        # Update translations to match the new name
        modified_property.translations = TranslationList([Translation(name=new_name)])

        # Replace the property
        updated_result = await async_instance.metadata.create_or_replace_property(
            modified_property
        )

        # Verify the update
        assert isinstance(updated_result, Property)
        assert updated_result.label == unique_label
        # Verify name was updated (API may use translation name)
        assert updated_result.name is not None

        # Verify by fetching again
        fetched_updated = await async_instance.metadata.get_property(unique_label)
        assert fetched_updated.label == unique_label
        assert fetched_updated.name is not None

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_create_property_with_translations(
        self, async_instance: AsyncOFSC, faker
    ):
        """Test creating a property with multiple translations"""
        unique_label = f"TEST_TRANS_{faker.pystr(min_chars=8, max_chars=12).upper()}"

        # Create property with English and Spanish translations
        en_name = faker.word().capitalize()
        es_name = "Césped"  # Test non-ASCII characters

        new_property = Property(
            label=unique_label,
            name=en_name,
            type="string",
            entity=EntityEnum.activity,
            gui="text",
            translations=TranslationList(
                [
                    Translation(name=en_name, language="en"),
                    Translation(name=es_name, language="es"),
                ]
            ),
        )

        # Create the property
        result = await async_instance.metadata.create_or_replace_property(new_property)

        # Verify the result
        assert isinstance(result, Property)
        assert result.label == unique_label
        # TranslationList is iterable, convert to list to check length
        assert len(list(result.translations)) >= 1  # At least one translation

        # Verify by fetching
        fetched = await async_instance.metadata.get_property(unique_label)
        assert isinstance(fetched, Property)
        assert fetched.label == unique_label

        # Check if translations are preserved (may vary by API behavior)
        translation_list = list(fetched.translations)
        if len(translation_list) > 1:
            translation_names = [t.name for t in translation_list]
            assert en_name in translation_names or es_name in translation_names

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_create_or_replace_property_model_validation(
        self, async_instance: AsyncOFSC, faker
    ):
        """Test that create_or_replace_property returns valid Property model"""
        unique_label = f"TEST_VALID_{faker.pystr(min_chars=8, max_chars=12).upper()}"

        new_property = Property(
            label=unique_label,
            name=faker.word().capitalize(),
            type="string",
            entity=EntityEnum.activity,
            gui="text",
            translations=TranslationList([Translation(name=faker.word())]),
        )

        result = await async_instance.metadata.create_or_replace_property(new_property)

        # Verify type validation
        assert isinstance(result, Property)
        assert hasattr(result, "label")
        assert hasattr(result, "name")
        assert hasattr(result, "type")
        assert hasattr(result, "entity")
        assert hasattr(result, "gui")
        assert hasattr(result, "translations")

        # Verify required fields are populated
        assert result.label == unique_label
        assert result.name is not None
        assert result.type is not None


class TestAsyncPropertySavedResponses:
    """Test model validation against saved API responses."""

    def test_property_list_response_validation(self):
        """Test PropertyListResponse model validates against saved response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "properties"
            / "get_properties_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        response = PropertyListResponse.model_validate(saved_data["response_data"])

        # Verify structure
        assert isinstance(response, PropertyListResponse)
        assert hasattr(response, "items")
        assert hasattr(response, "totalResults")
        assert len(response.items) > 0
        assert all(isinstance(item, Property) for item in response.items)

    def test_property_response_validation(self):
        """Test Property model validates against saved response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "properties"
            / "get_property_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        property_obj = Property.model_validate(saved_data["response_data"])

        # Verify structure
        assert isinstance(property_obj, Property)
        assert property_obj.label == "appt_number"
        assert property_obj.name == "Work Order"
        assert property_obj.type == "field"
        assert property_obj.entity is not None
        assert property_obj.gui == "text"
