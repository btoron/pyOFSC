"""Async tests for language operations."""

import json
from pathlib import Path

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.models import Language, LanguageListResponse


class TestAsyncGetLanguagesLive:
    """Live tests against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_languages(self, async_instance: AsyncOFSC):
        """Test get_languages with actual API - validates structure"""
        languages = await async_instance.metadata.get_languages()

        # Verify type validation
        assert isinstance(languages, LanguageListResponse)
        assert languages.totalResults is not None
        assert languages.totalResults >= 0
        assert hasattr(languages, "items")
        assert isinstance(languages.items, list)

        # Verify at least one language exists
        if len(languages.items) > 0:
            assert isinstance(languages.items[0], Language)


class TestAsyncGetLanguages:
    """Test async get_languages method."""

    @pytest.mark.asyncio
    async def test_get_languages_with_model(self, async_instance: AsyncOFSC):
        """Test that get_languages returns LanguageListResponse model"""
        languages = await async_instance.metadata.get_languages()

        # Verify type validation
        assert isinstance(languages, LanguageListResponse)
        assert hasattr(languages, "items")
        assert hasattr(languages, "totalResults")
        assert isinstance(languages.items, list)

        # Verify items are Language instances
        if len(languages.items) > 0:
            assert isinstance(languages.items[0], Language)
            assert hasattr(languages.items[0], "label")
            assert hasattr(languages.items[0], "code")
            assert hasattr(languages.items[0], "name")
            assert hasattr(languages.items[0], "active")
            assert hasattr(languages.items[0], "translations")

    @pytest.mark.asyncio
    async def test_get_languages_pagination(self, async_instance: AsyncOFSC):
        """Test get_languages with pagination"""
        languages = await async_instance.metadata.get_languages(offset=0, limit=2)
        assert isinstance(languages, LanguageListResponse)
        assert languages.totalResults is not None

    @pytest.mark.asyncio
    async def test_get_languages_total_results(self, async_instance: AsyncOFSC):
        """Test that totalResults is populated"""
        languages = await async_instance.metadata.get_languages()
        assert languages.totalResults is not None
        assert isinstance(languages.totalResults, int)
        assert languages.totalResults >= 0

    @pytest.mark.asyncio
    async def test_get_languages_field_types(self, async_instance: AsyncOFSC):
        """Test that language fields have correct types"""
        languages = await async_instance.metadata.get_languages()

        if len(languages.items) > 0:
            language = languages.items[0]
            assert isinstance(language.label, str)
            assert isinstance(language.code, str)
            assert isinstance(language.name, str)
            assert isinstance(language.active, bool)
            assert isinstance(language.translations, list)
            # Verify translation structure
            if len(language.translations) > 0:
                translation = language.translations[0]
                assert hasattr(translation, "language")
                assert hasattr(translation, "languageISO")
                assert hasattr(translation, "name")
                assert isinstance(translation.language, str)
                assert isinstance(translation.languageISO, str)
                assert isinstance(translation.name, str)


class TestAsyncLanguageSavedResponses:
    """Test model validation against saved API responses."""

    def test_language_list_response_validation(self):
        """Test LanguageListResponse model validates against saved response"""
        # Load saved response
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "languages"
            / "get_languages_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        # Validate the response_data can be parsed by the model
        response = LanguageListResponse.model_validate(saved_data["response_data"])

        # Verify structure
        assert isinstance(response, LanguageListResponse)
        assert hasattr(response, "items")
        assert hasattr(response, "totalResults")
        assert len(response.items) > 0
        assert all(isinstance(item, Language) for item in response.items)

        # Verify first language details
        first_language = response.items[0]
        assert isinstance(first_language, Language)
        assert first_language.label == "en-US"
        assert first_language.code == "en"
        assert first_language.name == "English"
        assert first_language.active is True
        assert isinstance(first_language.translations, list)
        assert len(first_language.translations) > 0

        # Verify first translation
        first_translation = first_language.translations[0]
        assert first_translation.language == "en"
        assert first_translation.languageISO == "en-US"
        assert first_translation.name == "English"
