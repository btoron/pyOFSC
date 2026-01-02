"""Tests for async daily extract operations."""

import json
from pathlib import Path

import pytest

from ofsc.async_client import AsyncOFSC
from ofsc.models import DailyExtractFiles, DailyExtractFolders


# ===================================================================
# GET DAILY EXTRACT DATES
# ===================================================================


class TestAsyncGetDailyExtractDatesLive:
    """Live tests for get_daily_extract_dates."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_daily_extract_dates(self, async_instance: AsyncOFSC):
        """Test get_daily_extract_dates with actual API."""
        result = await async_instance.core.get_daily_extract_dates()

        assert isinstance(result, DailyExtractFolders)
        assert hasattr(result, "name")
        assert result.name == "folders"
        assert hasattr(result, "folders")


# ===================================================================
# GET DAILY EXTRACT FILES
# ===================================================================


class TestAsyncGetDailyExtractFilesLive:
    """Live tests for get_daily_extract_files."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_daily_extract_files(self, async_instance: AsyncOFSC):
        """Test get_daily_extract_files with actual API - requires valid date."""
        # First get available dates
        dates_result = await async_instance.core.get_daily_extract_dates()

        # Skip test if no dates available
        if not dates_result.folders or not dates_result.folders.items:
            pytest.skip("No daily extract dates available")

        # Get files for the first available date
        first_date = dates_result.folders.items[0].name
        result = await async_instance.core.get_daily_extract_files(first_date)

        assert isinstance(result, DailyExtractFiles)
        assert hasattr(result, "name")
        assert result.name == "files"
        assert hasattr(result, "files")


# ===================================================================
# GET DAILY EXTRACT FILE
# ===================================================================


class TestAsyncGetDailyExtractFileLive:
    """Live tests for get_daily_extract_file."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_get_daily_extract_file_signature(self, async_instance: AsyncOFSC):
        """Test get_daily_extract_file returns bytes - signature test only."""
        # First get available dates
        dates_result = await async_instance.core.get_daily_extract_dates()

        # Skip test if no dates available
        if not dates_result.folders or not dates_result.folders.items:
            pytest.skip("No daily extract dates available")

        # Get files for the first available date
        first_date = dates_result.folders.items[0].name
        files_result = await async_instance.core.get_daily_extract_files(first_date)

        # Skip if no files available
        if not files_result.files or not files_result.files.items:
            pytest.skip("No daily extract files available")

        # Get the first file
        first_file = files_result.files.items[0].name
        result = await async_instance.core.get_daily_extract_file(
            first_date, first_file
        )

        # Verify it returns bytes
        assert isinstance(result, bytes)
        # Don't verify content since we're just testing signature


# ===================================================================
# SAVED RESPONSE VALIDATION
# ===================================================================


class TestAsyncDailyExtractSavedResponses:
    """Test model validation against saved API responses."""

    def test_daily_extract_dates_response_validation(self):
        """Test DailyExtractFolders validates against saved response."""
        saved_response_path = (
            Path(__file__).parent.parent
            / "saved_responses"
            / "daily_extracts"
            / "get_daily_extract_dates_200_success.json"
        )

        with open(saved_response_path) as f:
            saved_data = json.load(f)

        response = DailyExtractFolders.model_validate(saved_data["response_data"])

        assert isinstance(response, DailyExtractFolders)
        assert response.name == "folders"
        assert hasattr(response, "folders")
