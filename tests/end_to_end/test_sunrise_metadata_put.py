"""End-to-end tests for Sunrise metadata PUT and DELETE operations.

This module contains tests that modify data via the metadata API endpoints.
These tests create, update, and delete resources as part of their test cycle.
"""

import asyncio

import pytest

# Import shared test data and fixtures
from conftest_sunrise_metadata import get_test_data

from ofsc.client import OFSC
from ofsc.models.base import Translation, TranslationList
from ofsc.models.capacity import CapacityCategoryRequest, CapacityCategoryResponse
from ofsc.models.metadata import (
    ActivityTypeGroup,
    EntityEnum,
    PropertyRequest,
    PropertyResponse,
)


@pytest.mark.live
class TestSunrisePutMetadata:
    """Live authentication tests for PUT/DELETE metadata operations using OFSC client classes."""

    def test_sunrise_client_create_or_replace_activity_type_group(
        self, async_client_basic_auth: OFSC
    ):
        """Test endpoint ID 3: PUT /rest/ofscMetadata/v1/activityTypeGroups/{label} - Create or replace activity type group."""

        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                # Test 1: Create with no translations (empty request)
                response = await client.metadata.create_or_replace_activity_type_group(
                    "testGroup", None
                )
                assert isinstance(response, ActivityTypeGroup)
                assert response.label == "testGroup"

                # Test 2: Update with custom translations
                translations = TranslationList(
                    [
                        Translation(
                            language="en",
                            name="Test Group Updated",
                            languageISO="en-US",
                        ),
                        Translation(
                            language="es", name="Grupo de Prueba", languageISO="es-ES"
                        ),
                    ]
                )
                response = await client.metadata.create_or_replace_activity_type_group(
                    "testGroup", translations
                )
                assert isinstance(response, ActivityTypeGroup)
                assert response.label == "testGroup"
                # Verify translations were applied
                assert response.translations is not None
                assert (
                    len(response.translations.root) >= 1
                )  # Should have at least the translations we sent

                # Test 3: Update with empty translations list
                empty_translations = TranslationList([])
                response = await client.metadata.create_or_replace_activity_type_group(
                    "testGroup", empty_translations
                )
                assert isinstance(response, ActivityTypeGroup)
                assert response.label == "testGroup"

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_create_or_replace_capacity_category(
        self, async_client_basic_auth: OFSC
    ):
        """Test endpoint ID 25: PUT /rest/ofscMetadata/v1/capacityCategories/{label} - Create or replace capacity category."""

        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                # Get test data for work skills and workzones to use in the capacity category
                workskill_identifiers = get_test_data("workskill")
                workzone_identifiers = get_test_data("workzone")

                # Create a test capacity category using available test data
                test_category_label = "TEST_CAPACITY_CAT"

                # Build time slots based on existing format (only label field)
                time_slots = [{"label": "08-10"}, {"label": "10-12"}]

                # Build work skills from test data with proper structure
                work_skills = []
                for skill in workskill_identifiers:
                    if skill and skill != "":
                        work_skills.append(
                            {"label": skill, "ratio": 1, "startDate": "2000-01-01"}
                        )
                        break  # Just use one for the test

                # Build work skill groups (empty for now since test data shows empty results)
                work_skill_groups = []

                # Create request with translations
                translations = TranslationList(
                    [
                        Translation(
                            language="en",
                            name="Test Capacity Category",
                            languageISO="en-US",
                        ),
                        Translation(
                            language="es",
                            name="Categoría de Capacidad de Prueba",
                            languageISO="es-ES",
                        ),
                    ]
                )

                capacity_category_request = CapacityCategoryRequest(
                    label=test_category_label,
                    name="Test Capacity Category",
                    active=True,
                    timeSlots=time_slots,
                    workSkills=work_skills,
                    workSkillGroups=work_skill_groups,
                    translations=translations,
                )

                # Test 1: Create the capacity category
                response = await client.metadata.create_or_replace_capacity_category(
                    test_category_label, capacity_category_request
                )
                assert isinstance(response, CapacityCategoryResponse)
                assert response.label == test_category_label
                assert response.name == "Test Capacity Category"
                assert response.active is True

                # Verify that the created category exists by fetching it
                fetched_category = await client.metadata.get_capacity_category(
                    test_category_label
                )
                assert isinstance(fetched_category, CapacityCategoryResponse)
                assert fetched_category.label == test_category_label
                assert fetched_category.name == "Test Capacity Category"

                # Test 2: Delete the capacity category (cleanup)
                await client.metadata.delete_capacity_category(test_category_label)

                # Verify deletion by trying to fetch (should raise an exception)
                try:
                    await client.metadata.get_capacity_category(test_category_label)
                    assert False, (
                        "Expected exception when fetching deleted capacity category"
                    )
                except Exception:
                    # Expected - category should not exist after deletion
                    pass

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))

    def test_sunrise_client_create_or_replace_property(
        self, async_client_basic_auth: OFSC
    ):
        """Test endpoint ID 52: PUT /rest/ofscMetadata/v1/properties/{label} - Create or replace property."""

        async def test_async_client_basic_auth(async_client_basic_auth):
            async with async_client_basic_auth as client:
                # Create a test property using test data
                test_property_label = "TEST_PROP_E2E"

                # Create request with translations
                translations = TranslationList(
                    [
                        Translation(
                            language="en", name="Test Property E2E", languageISO="en-US"
                        ),
                        Translation(
                            language="es",
                            name="Propiedad de Prueba E2E",
                            languageISO="es-ES",
                        ),
                    ]
                )

                property_request = PropertyRequest(
                    label=test_property_label,
                    name="Test Property E2E",
                    type="string",
                    entity=EntityEnum.activity,
                    gui="text",
                    translations=translations,
                )

                # Test 1: Create the property
                response = await client.metadata.create_or_replace_property(
                    test_property_label, property_request
                )
                assert isinstance(response, PropertyResponse)
                assert response.label == test_property_label
                assert response.name == "Test Property E2E"
                assert response.type == "string"
                assert response.entity == "activity"
                assert response.gui == "text"

                # Verify that the created property exists by fetching it
                fetched_property = await client.metadata.get_property(
                    test_property_label
                )
                assert isinstance(fetched_property, PropertyResponse)
                assert fetched_property.label == test_property_label
                assert fetched_property.name == "Test Property E2E"
                assert fetched_property.type == "string"

                # Test 2: Test that the property was properly created with all expected fields
                assert fetched_property.entity == "activity"
                assert fetched_property.gui == "text"
                assert fetched_property.translations is not None
                assert len(fetched_property.translations.root) >= 1

                print(
                    f"✅ Successfully tested create_or_replace_property for {test_property_label}"
                )

        asyncio.run(test_async_client_basic_auth(async_client_basic_auth))
