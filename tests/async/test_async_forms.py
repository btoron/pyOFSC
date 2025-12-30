"""Tests for async forms metadata methods."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import Form, FormListResponse


# === GET FORMS (LIST) ===


class TestAsyncGetFormsLive:
    """Live tests for get_forms against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_forms(self, async_instance: AsyncOFSC):
        """Test get_forms with actual API - validates structure."""
        result = await async_instance.metadata.get_forms()

        assert isinstance(result, FormListResponse)
        assert hasattr(result, "items")
        assert len(result.items) > 0

        # Validate first item structure
        first_form = result.items[0]
        assert isinstance(first_form, Form)
        assert hasattr(first_form, "label")
        assert hasattr(first_form, "name")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_forms_pagination(self, async_instance: AsyncOFSC):
        """Test get_forms with pagination."""
        result = await async_instance.metadata.get_forms(offset=0, limit=2)

        assert isinstance(result, FormListResponse)
        assert len(result.items) <= 2

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_all_forms_individually(self, async_instance: AsyncOFSC):
        """Test getting all forms individually to validate all configurations.

        This test:
        1. Retrieves all forms
        2. Iterates through each one
        3. Retrieves each form individually by label
        4. Validates that all models parse correctly

        This ensures the models can handle all real-world configuration variations.
        """
        # First get all forms
        all_forms = await async_instance.metadata.get_forms()

        assert isinstance(all_forms, FormListResponse)
        assert len(all_forms.items) > 0

        # Track results for reporting
        successful = 0
        failed = []

        # Iterate through each form and get it individually
        for form in all_forms.items:
            try:
                individual_form = await async_instance.metadata.get_form(form.label)

                # Validate the returned form
                assert isinstance(individual_form, Form)
                assert individual_form.label == form.label

                successful += 1
            except Exception as e:
                failed.append({"label": form.label, "error": str(e)})

        # Report results
        print("\nForms validation:")
        print(f"  Total forms: {len(all_forms.items)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {len(failed)}")

        if failed:
            print("\nFailed forms:")
            for failure in failed:
                print(f"  - {failure['label']}: {failure['error']}")

        # All forms should be retrieved successfully
        assert len(failed) == 0, f"Failed to retrieve {len(failed)} forms: {failed}"
        assert successful == len(all_forms.items)


class TestAsyncGetFormsModel:
    """Model validation tests for get_forms."""

    @pytest.mark.asyncio
    async def test_get_forms_returns_model(self, async_instance: AsyncOFSC):
        """Test that get_forms returns FormListResponse model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "label": "test_form",
                    "name": "Test Form",
                    "translations": [
                        {"language": "en", "name": "Test Form", "languageISO": "en-US"}
                    ],
                },
                {
                    "label": "another_form",
                    "name": "Another Form",
                    "translations": [
                        {
                            "language": "en",
                            "name": "Another Form",
                            "languageISO": "en-US",
                        }
                    ],
                },
            ],
            "totalResults": 2,
            "links": [],
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_forms()

        assert isinstance(result, FormListResponse)
        assert len(result.items) == 2
        assert result.items[0].label == "test_form"
        assert result.items[1].label == "another_form"

    @pytest.mark.asyncio
    async def test_get_forms_field_types(self, async_instance: AsyncOFSC):
        """Test that fields have correct types."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "label": "TEST_FORM",
                    "name": "Test Form",
                    "translations": [
                        {"language": "en", "name": "Test Form", "languageISO": "en-US"}
                    ],
                }
            ],
            "totalResults": 1,
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_forms()

        assert isinstance(result.items[0].label, str)
        assert isinstance(result.items[0].name, str)


# === GET FORM (SINGLE) ===


class TestAsyncGetFormLive:
    """Live tests for get_form against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_form(self, async_instance: AsyncOFSC):
        """Test get_form with actual API."""
        # First get all forms to find a valid label
        forms = await async_instance.metadata.get_forms()
        assert len(forms.items) > 0

        # Get the first form by label
        test_label = forms.items[0].label
        result = await async_instance.metadata.get_form(test_label)

        assert isinstance(result, Form)
        assert result.label == test_label
        # Single form should include content field
        assert hasattr(result, "content")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_form_not_found(self, async_instance: AsyncOFSC):
        """Test get_form with non-existent label."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_form("NONEXISTENT_FORM_12345")


class TestAsyncGetFormModel:
    """Model validation tests for get_form."""

    @pytest.mark.asyncio
    async def test_get_form_returns_model(self, async_instance: AsyncOFSC):
        """Test that get_form returns Form model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "label": "TEST_FORM",
            "name": "Test Form",
            "translations": [
                {"language": "en", "name": "Test Form", "languageISO": "en-US"}
            ],
            "content": '{"formatVersion":"1.1","items":[]}',
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_form("TEST_FORM")

        assert isinstance(result, Form)
        assert result.label == "TEST_FORM"
        assert result.name == "Test Form"
        assert result.content is not None


# === SAVED RESPONSE VALIDATION ===


class TestAsyncFormsSavedResponses:
    """Test that saved API responses validate against Pydantic models."""

    def test_form_list_response_validation(self):
        """Test FormListResponse model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "forms"
            / "get_forms_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = FormListResponse.model_validate(saved_data["response_data"])

        assert isinstance(response, FormListResponse)
        assert response.totalResults == 16  # From the captured data
        assert len(response.items) == 16
        assert all(isinstance(form, Form) for form in response.items)

    def test_form_single_validation(self):
        """Test Form model validates against saved single response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "forms"
            / "get_form_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        form = Form.model_validate(saved_data["response_data"])

        assert isinstance(form, Form)
        assert form.label == "case"
        assert form.name == "Case"
        assert form.content is not None
        assert form.translations is not None
        assert len(form.translations.root) == 2
