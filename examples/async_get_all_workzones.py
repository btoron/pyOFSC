#!/usr/bin/env python3
"""Example: iterate all workzones lazily with get_all_workzones.

This example demonstrates:
- Using the async generator get_all_workzones()
- Lazy pagination — pages are fetched on demand as you iterate
- Collecting results vs. processing one-by-one
"""

import asyncio
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from config import Config

from ofsc.async_client import AsyncOFSC


async def main():
    async with AsyncOFSC(
        clientID=Config.OFSC_CLIENT_ID,
        secret=Config.OFSC_CLIENT_SECRET,
        companyName=Config.OFSC_COMPANY,
        root=Config.OFSC_ROOT,
    ) as client:
        print("Iterating workzones one by one (lazy):")
        count = 0
        async for workzone in client.metadata.get_all_workzones(limit=10):
            print(f"  [{count + 1}] {workzone.workZoneLabel}: {workzone.workZoneName}")
            count += 1

        print(f"\nTotal workzones yielded: {count}")

        # You can also collect into a list with an async comprehension
        all_labels = [
            wz.workZoneLabel
            async for wz in client.metadata.get_all_workzones(limit=10)
        ]
        print(f"Labels collected: {all_labels}")


if __name__ == "__main__":
    asyncio.run(main())
