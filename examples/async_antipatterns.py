#!/usr/bin/env python3
"""AsyncOFSC antipatterns - DO NOT USE THESE PATTERNS!

This example demonstrates UNSAFE patterns that will cause problems:
❌ Mixing threading with AsyncClient
❌ Sharing AsyncOFSC across event loops
❌ Creating multiple event loops

These patterns are shown for educational purposes only.
For safe parallel execution, see async_parallel_requests.py
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor  # noqa: F401
from logging import basicConfig
from pathlib import Path
from threading import Thread  # noqa: F401

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from config import Config

from ofsc.async_client import AsyncOFSC


# ❌ ANTIPATTERN 1: Using ThreadPoolExecutor with AsyncClient
async def antipattern_threading():
    """
    ❌ UNSAFE: Trying to use ThreadPoolExecutor with async client.

    Problem:
    - Each thread would need its own event loop
    - AsyncClient cannot be shared across event loops
    - Will cause hangs, race conditions, or crashes

    What happens:
    - asyncio.run() creates a new event loop per thread
    - Multiple event loops try to share the same AsyncClient
    - httpx's async primitives are not thread-safe
    """
    logging.warning("⚠️  ANTIPATTERN 1: ThreadPoolExecutor + AsyncClient")

    # Note: baseUrl defaults to https://{companyName}.fs.ocs.oraclecloud.com
    async with AsyncOFSC(
        clientID=Config.OFSC_CLIENT_ID,
        secret=Config.OFSC_CLIENT_SECRET,
        companyName=Config.OFSC_COMPANY,
        root=Config.OFSC_ROOT,
    ) as client:

        def threaded_call():
            """This will fail or hang!"""
            # DON'T DO THIS: Creates new event loop in thread
            return asyncio.run(client.metadata.get_workzones())

        # This pattern is UNSAFE and will likely fail
        # Uncomment to see the problem (may hang indefinitely):
        # with ThreadPoolExecutor(max_workers=3) as executor:
        #     futures = [executor.submit(threaded_call) for _ in range(3)]
        #     results = [f.result() for f in futures]

        logging.error("This pattern is commented out because it will hang or crash!")


# ❌ ANTIPATTERN 2: Sharing client across threads
def antipattern_shared_client():
    """
    ❌ UNSAFE: Creating client in one thread, using in others.

    Problem:
    - AsyncOFSC is tied to a single event loop
    - Cannot be shared across threads safely
    - Event loop is specific to the thread where asyncio.run() is called
    """
    logging.warning("⚠️  ANTIPATTERN 2: Shared AsyncOFSC across threads")

    # DON'T DO THIS
    client_container = {"client": None}

    async def create_client():
        """Create client in main thread."""
        async with AsyncOFSC(
            clientID=Config.OFSC_CLIENT_ID,
            secret=Config.OFSC_CLIENT_SECRET,
            companyName=Config.OFSC_COMPANY,
            baseUrl=Config.OFSC_BASE_URL,
        ) as client:
            client_container["client"] = client
            # Keep client alive for threads
            await asyncio.sleep(5)

    def use_client_in_thread():
        """Try to use client in different thread - WILL FAIL."""
        client = client_container["client"]  # noqa: F841
        # This will fail - client is tied to different event loop
        # return asyncio.run(client.metadata.get_workzones())

    # Don't actually run this - it will fail
    logging.error("This pattern would fail because client is tied to one event loop!")


# ✅ CORRECT PATTERN: One event loop, asyncio.gather
async def correct_pattern():
    """
    ✅ SAFE: Use asyncio.gather() in the same event loop.

    Benefits:
    - Single event loop
    - Single thread (async concurrency, not parallelism)
    - HTTP/2 multiplexing handles concurrent requests efficiently
    - No race conditions or threading issues
    """
    logging.info("✅ CORRECT PATTERN: asyncio.gather()")

    # Note: baseUrl defaults to https://{companyName}.fs.ocs.oraclecloud.com
    async with AsyncOFSC(
        clientID=Config.OFSC_CLIENT_ID,
        secret=Config.OFSC_CLIENT_SECRET,
        companyName=Config.OFSC_COMPANY,
        root=Config.OFSC_ROOT,
    ) as client:
        # This is the RIGHT way to parallelize
        workzones, activity_types = await asyncio.gather(
            client.metadata.get_workzones(),
            client.metadata.get_activity_types(),
        )

        logging.info(f"✅ Successfully fetched {workzones.totalResults} workzones")
        logging.info(
            f"✅ Successfully fetched {activity_types.totalResults} activity types"
        )


async def main():
    """Demonstrate antipatterns and correct usage."""
    basicConfig(level=logging.INFO)

    print("\n" + "=" * 70)
    print("ASYNC CLIENT PATTERNS - EDUCATIONAL EXAMPLES")
    print("=" * 70 + "\n")

    # Show antipatterns (without actually running them)
    await antipattern_threading()
    antipattern_shared_client()

    print("\n" + "=" * 70)
    print("NOW SHOWING THE CORRECT PATTERN:")
    print("=" * 70 + "\n")

    # Show correct pattern
    await correct_pattern()

    print("\n" + "=" * 70)
    print("SUMMARY:")
    print("=" * 70)
    print("❌ DON'T: Use ThreadPoolExecutor with AsyncClient")
    print("❌ DON'T: Share AsyncOFSC across threads or event loops")
    print("✅ DO: Use asyncio.gather() in the same event loop")
    print("✅ DO: See async_parallel_requests.py for working examples")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
