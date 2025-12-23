"""Async test fixtures."""

import os

import pytest
from dotenv import load_dotenv

from ofsc.async_client import AsyncOFSC


@pytest.fixture
async def async_instance():
    """Create an async OFSC instance for testing."""
    load_dotenv()
    async with AsyncOFSC(
        clientID=os.environ.get("OFSC_CLIENT_ID"),
        secret=os.environ.get("OFSC_CLIENT_SECRET"),
        companyName=os.environ.get("OFSC_COMPANY"),
        root=os.environ.get("OFSC_ROOT"),
    ) as instance:
        yield instance
