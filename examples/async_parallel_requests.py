#!/usr/bin/env python3
"""Parallel API requests using asyncio.gather.

This example demonstrates the SAFE way to parallelize API calls with AsyncOFSC:
- Using asyncio.gather() for concurrent requests
- Single event loop, no threading
- HTTP/2 multiplexing for efficient network usage

Performance comparison:
- Sequential: 3 requests × 500ms = ~1500ms
- Parallel: max(500ms, 500ms, 500ms) = ~500ms (3× faster)
"""

import asyncio
import logging
import time
from logging import basicConfig
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from config import Config

from ofsc.async_client import AsyncOFSC


async def sequential_requests(client: AsyncOFSC):
    """Fetch metadata sequentially (slower)."""
    start = time.time()

    workzones = await client.metadata.get_workzones()
    activity_types = await client.metadata.get_activity_types()
    inventory_types = await client.metadata.get_inventory_types()

    elapsed = time.time() - start
    logging.info(f"Sequential: {elapsed:.2f}s")

    return workzones, activity_types, inventory_types


async def parallel_requests(client: AsyncOFSC):
    """Fetch metadata in parallel (faster)."""
    start = time.time()

    # ✅ SAFE: asyncio.gather() runs coroutines concurrently in the same event loop
    workzones, activity_types, inventory_types = await asyncio.gather(
        client.metadata.get_workzones(),
        client.metadata.get_activity_types(),
        client.metadata.get_inventory_types(),
    )

    elapsed = time.time() - start
    logging.info(f"Parallel: {elapsed:.2f}s")

    return workzones, activity_types, inventory_types


async def main():
    """Compare sequential vs parallel API calls."""
    basicConfig(level=logging.INFO)

    # Note: baseUrl defaults to https://{companyName}.fs.ocs.oraclecloud.com
    async with AsyncOFSC(
        clientID=Config.OFSC_CLIENT_ID,
        secret=Config.OFSC_CLIENT_SECRET,
        companyName=Config.OFSC_COMPANY,
        root=Config.OFSC_ROOT,
    ) as client:
        logging.info(f"Connected to {Config.OFSC_COMPANY}\n")

        # Sequential execution
        logging.info("=== Sequential Requests ===")
        seq_results = await sequential_requests(client)
        print(f"Workzones: {seq_results[0].totalResults}")
        print(f"Activity Types: {seq_results[1].totalResults}")
        print(f"Inventory Types: {seq_results[2].totalResults}\n")

        # Parallel execution
        logging.info("=== Parallel Requests (asyncio.gather) ===")
        par_results = await parallel_requests(client)
        print(f"Workzones: {par_results[0].totalResults}")
        print(f"Activity Types: {par_results[1].totalResults}")
        print(f"Inventory Types: {par_results[2].totalResults}\n")

        # Demonstrate error handling with gather
        logging.info("=== Error Handling with gather ===")
        try:
            results = await asyncio.gather(
                client.metadata.get_workzone("EXISTING_ZONE"),
                client.metadata.get_workzone(
                    "NONEXISTENT_ZONE_12345"
                ),  # Will raise 404
                return_exceptions=True,  # Collect exceptions instead of raising
            )

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logging.error(f"Request {i} failed: {result}")
                else:
                    logging.info(f"Request {i} succeeded: {result.label}")

        except Exception as e:
            logging.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
