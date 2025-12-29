"""Tests for async plugins metadata methods."""

from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from ofsc.async_client import AsyncOFSC


class TestAsyncImportPluginFileLive:
    """Live tests for import_plugin_file against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_import_plugin_file(self, async_instance: AsyncOFSC):
        """Test import_plugin_file with actual API.

        Note: Requires a valid OFSC plugin XML file. The test.xml file
        is a placeholder and will fail validation. Replace with a real
        OFSC plugin export to test successfully.
        """
        plugin_path = Path("tests/test.xml")
        if not plugin_path.exists():
            pytest.skip("Test plugin file not found")

        # Skip if using placeholder test file (expected to fail)
        pytest.skip("Requires valid OFSC plugin XML (test.xml is placeholder)")

        result = await async_instance.metadata.import_plugin_file(plugin_path)
        assert result is None  # 204 No Content


class TestAsyncImportPluginLive:
    """Live tests for import_plugin against actual API."""

    @pytest.mark.asyncio
    @pytest.mark.uses_real_data
    async def test_import_plugin(self, async_instance: AsyncOFSC):
        """Test import_plugin with actual API.

        Note: Requires a valid OFSC plugin XML file. The test.xml file
        is a placeholder and will fail validation. Replace with a real
        OFSC plugin export to test successfully.
        """
        plugin_path = Path("tests/test.xml")
        if not plugin_path.exists():
            pytest.skip("Test plugin file not found")

        # Skip if using placeholder test file (expected to fail)
        pytest.skip("Requires valid OFSC plugin XML (test.xml is placeholder)")

        plugin_content = plugin_path.read_text()
        result = await async_instance.metadata.import_plugin(plugin_content)
        assert result is None  # 204 No Content


class TestAsyncImportPluginFileMock:
    """Mock tests for import_plugin_file."""

    @pytest.mark.asyncio
    async def test_import_plugin_file_success(self, async_instance: AsyncOFSC):
        """Test import_plugin_file returns None on 204."""
        mock_response = Mock()
        mock_response.status_code = 204

        async_instance.metadata._client.post = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.import_plugin_file(
            Path("tests/test.xml")
        )

        assert result is None


class TestAsyncImportPluginMock:
    """Mock tests for import_plugin."""

    @pytest.mark.asyncio
    async def test_import_plugin_success(self, async_instance: AsyncOFSC):
        """Test import_plugin returns None on 204."""
        mock_response = Mock()
        mock_response.status_code = 204

        async_instance.metadata._client.post = AsyncMock(return_value=mock_response)
        result = await async_instance.metadata.import_plugin("<plugin></plugin>")

        assert result is None
