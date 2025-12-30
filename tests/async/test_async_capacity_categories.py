"""Tests for async capacity categories metadata methods."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.exceptions import OFSCNotFoundError
from ofsc.models import CapacityCategory, CapacityCategoryListResponse


# === GET CAPACITY CATEGORIES (LIST) ===


class TestAsyncGetCapacityCategoriesLive:
    """Live tests for get_capacity_categories against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_categories(self, async_instance: AsyncOFSC):
        """Test get_capacity_categories with actual API - validates structure."""
        result = await async_instance.metadata.get_capacity_categories()

        assert isinstance(result, CapacityCategoryListResponse)
        assert hasattr(result, "items")
        assert len(result.items) > 0

        # Validate first item structure
        first_category = result.items[0]
        assert isinstance(first_category, CapacityCategory)
        assert hasattr(first_category, "label")

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_categories_pagination(self, async_instance: AsyncOFSC):
        """Test get_capacity_categories with pagination."""
        result = await async_instance.metadata.get_capacity_categories(
            offset=0, limit=2
        )

        assert isinstance(result, CapacityCategoryListResponse)
        assert len(result.items) <= 2

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_all_capacity_categories_individually(
        self, async_instance: AsyncOFSC
    ):
        """Test getting all capacity categories individually to validate all configurations.

        This test:
        1. Retrieves all capacity categories
        2. Iterates through each one
        3. Retrieves each category individually by label
        4. Validates that all models parse correctly

        This ensures the models can handle all real-world configuration variations.
        """
        # First get all capacity categories
        all_categories = await async_instance.metadata.get_capacity_categories()

        assert isinstance(all_categories, CapacityCategoryListResponse)
        assert len(all_categories.items) > 0

        # Track results for reporting
        successful = 0
        failed = []

        # Iterate through each category and get it individually
        for category in all_categories.items:
            try:
                individual_category = (
                    await async_instance.metadata.get_capacity_category(category.label)
                )

                # Validate the returned category
                assert isinstance(individual_category, CapacityCategory)
                assert individual_category.label == category.label

                successful += 1
            except Exception as e:
                failed.append({"label": category.label, "error": str(e)})

        # Report results
        print("\nCapacity Categories validation:")
        print(f"  Total categories: {len(all_categories.items)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {len(failed)}")

        if failed:
            print("\nFailed categories:")
            for failure in failed:
                print(f"  - {failure['label']}: {failure['error']}")

        # All categories should be retrieved successfully
        assert len(failed) == 0, (
            f"Failed to retrieve {len(failed)} categories: {failed}"
        )
        assert successful == len(all_categories.items)


class TestAsyncGetCapacityCategoriesModel:
    """Model validation tests for get_capacity_categories."""

    @pytest.mark.asyncio
    async def test_get_capacity_categories_returns_model(
        self, async_instance: AsyncOFSC
    ):
        """Test that get_capacity_categories returns CapacityCategoryListResponse model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"label": "CAT1", "name": "Category 1", "active": True},
                {"label": "CAT2", "name": "Category 2", "active": True},
            ],
            "totalResults": 2,
            "links": [],
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_capacity_categories()

        assert isinstance(result, CapacityCategoryListResponse)
        assert len(result.items) == 2
        assert result.items[0].label == "CAT1"
        assert result.items[1].label == "CAT2"

    @pytest.mark.asyncio
    async def test_get_capacity_categories_field_types(self, async_instance: AsyncOFSC):
        """Test that fields have correct types."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"label": "TEST_CAT", "name": "Test Category", "active": True}],
            "totalResults": 1,
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_capacity_categories()

        assert isinstance(result.items[0].label, str)
        assert isinstance(result.items[0].active, bool)


# === GET CAPACITY CATEGORY (SINGLE) ===


class TestAsyncGetCapacityCategoryLive:
    """Live tests for get_capacity_category against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_category(self, async_instance: AsyncOFSC):
        """Test get_capacity_category with actual API."""
        # First get all categories to find a valid label
        categories = await async_instance.metadata.get_capacity_categories()
        assert len(categories.items) > 0

        # Get the first category by label
        test_label = categories.items[0].label
        result = await async_instance.metadata.get_capacity_category(test_label)

        assert isinstance(result, CapacityCategory)
        assert result.label == test_label

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_capacity_category_not_found(self, async_instance: AsyncOFSC):
        """Test get_capacity_category with non-existent label."""
        with pytest.raises(OFSCNotFoundError):
            await async_instance.metadata.get_capacity_category(
                "NONEXISTENT_CATEGORY_12345"
            )


class TestAsyncGetCapacityCategoryModel:
    """Model validation tests for get_capacity_category."""

    @pytest.mark.asyncio
    async def test_get_capacity_category_returns_model(self, async_instance: AsyncOFSC):
        """Test that get_capacity_category returns CapacityCategory model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "label": "TEST_CAT",
            "name": "Test Category",
            "active": True,
        }

        async_instance.metadata._client.get = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.get_capacity_category("TEST_CAT")

        assert isinstance(result, CapacityCategory)
        assert result.label == "TEST_CAT"
        assert result.name == "Test Category"


# === SAVED RESPONSE VALIDATION ===


class TestAsyncCapacityCategoriesSavedResponses:
    """Test that saved API responses validate against Pydantic models."""

    def test_capacity_category_list_response_validation(self):
        """Test CapacityCategoryListResponse model validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "capacity_categories"
            / "get_capacity_categories_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = CapacityCategoryListResponse.model_validate(
            saved_data["response_data"]
        )

        assert isinstance(response, CapacityCategoryListResponse)
        assert response.totalResults == 3  # From the captured data
        assert len(response.items) == 3
        assert all(isinstance(cat, CapacityCategory) for cat in response.items)

    def test_capacity_category_single_validation(self):
        """Test CapacityCategory model validates against saved single response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "capacity_categories"
            / "get_capacity_category_200_success.json"
        )
        with open(saved_response_path) as f:
            saved_data = json.load(f)

        category = CapacityCategory.model_validate(saved_data["response_data"])

        assert isinstance(category, CapacityCategory)
        assert category.label == "EST"
        assert category.name == "Estimate"
        assert category.active is True
