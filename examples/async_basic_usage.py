#!/usr/bin/env python3
"""Basic async client usage example.

This example demonstrates:
- Creating an AsyncOFSC client instance
- Using the async context manager pattern
- Making simple async API calls
"""

import asyncio
import logging
from logging import basicConfig
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from config import Config

from ofsc.async_client import AsyncOFSC


async def main():
    """Fetch workzones using the async client."""
    basicConfig(level=logging.INFO)

    # AsyncOFSC must be used as an async context manager
    # Note: baseUrl defaults to https://{companyName}.fs.ocs.oraclecloud.com
    async with AsyncOFSC(
        clientID=Config.OFSC_CLIENT_ID,
        secret=Config.OFSC_CLIENT_SECRET,
        companyName=Config.OFSC_COMPANY,
        root=Config.OFSC_ROOT,
    ) as client:
        logging.info(f"Connected to {Config.OFSC_COMPANY}")

        # Make async API calls
        workzones = await client.metadata.get_workzones()
        logging.info(f"Found {workzones.totalResults} workzones")

        # Print first few workzones
        for wz in workzones.items[:5]:
            print(f"  - {wz.workZoneLabel}: {wz.workZoneName}")

        # Fetch activity types
        activity_types = await client.metadata.get_activity_types()
        logging.info(f"Found {activity_types.totalResults} activity types")

        for at in activity_types.items[:5]:
            print(f"  - {at.label}: {at.name}")


if __name__ == "__main__":
    asyncio.run(main())
