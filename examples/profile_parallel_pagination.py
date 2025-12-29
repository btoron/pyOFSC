#!/usr/bin/env python3
"""Profile where time is spent in parallel pagination.

This example breaks down the parallel pagination approach into detailed timing
components to identify optimization opportunities:
- Network I/O time
- Pydantic validation time
- JSON parsing time
- Other overhead

Run 20 iterations to get reliable statistics.
"""

import asyncio
import statistics
import time
from math import ceil
from pathlib import Path
from urllib.parse import urljoin

from dotenv import load_dotenv

# Load environment variables from .env file BEFORE importing Config
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from config import Config  # noqa: E402
from ofsc.async_client import AsyncOFSC  # noqa: E402
from ofsc.models import PropertyListResponse  # noqa: E402


async def profile_parallel_approach(client: AsyncOFSC, iterations: int = 20):
    """Profile where time is spent in parallel pagination."""

    results = {
        "phase1_network": [],  # Time to get first page (before validation)
        "phase1_validation": [],  # Time to validate first page
        "phase2_network": [],  # Time for parallel requests (before validation)
        "phase2_validation": [],  # Time to validate all parallel responses
        "total": [],
    }

    # Prepare URL and params
    base_url = client.metadata.baseUrl
    headers = client.metadata.headers
    url = urljoin(base_url, "/rest/ofscMetadata/v1/properties")
    page_size = 100

    for i in range(iterations):
        total_start = time.time()

        # ================================================================
        # Phase 1: First retrieval (limit=100 to get count + 100 items)
        # ================================================================
        network_start = time.time()
        response = await client._client.get(
            url, headers=headers, params={"offset": 0, "limit": page_size}
        )
        data = response.json()
        phase1_network = time.time() - network_start

        # Phase 1: Validation
        validation_start = time.time()
        first_page = PropertyListResponse.model_validate(data)
        phase1_validation = time.time() - validation_start

        total_items = first_page.totalResults
        total_pages = ceil(total_items / page_size)

        # ================================================================
        # Phase 2: Parallel retrievals (remaining pages)
        # ================================================================
        # Define helper to fetch raw response (defer validation)
        async def fetch_raw(offset: int):
            resp = await client._client.get(
                url, headers=headers, params={"offset": offset, "limit": page_size}
            )
            return resp.json()

        # Fetch all remaining pages in parallel (defer validation)
        offsets = [i * page_size for i in range(1, total_pages)]

        network_start = time.time()
        raw_responses = await asyncio.gather(
            *[fetch_raw(offset) for offset in offsets], return_exceptions=True
        )
        phase2_network = time.time() - network_start

        # Phase 2: Validation (validate all responses)
        validation_start = time.time()
        pages = []
        for raw_data in raw_responses:
            if isinstance(raw_data, Exception):
                continue
            try:
                page = PropertyListResponse.model_validate(raw_data)
                pages.append(page)
            except Exception:
                continue  # Skip validation errors
        phase2_validation = time.time() - validation_start

        # Record timing
        total_time = time.time() - total_start
        results["phase1_network"].append(phase1_network)
        results["phase1_validation"].append(phase1_validation)
        results["phase2_network"].append(phase2_network)
        results["phase2_validation"].append(phase2_validation)
        results["total"].append(total_time)

        # Progress indicator
        print(
            f"Iteration {i+1:2}/{iterations}: "
            f"P1N={phase1_network:.3f}s P1V={phase1_validation:.3f}s "
            f"P2N={phase2_network:.3f}s P2V={phase2_validation:.3f}s "
            f"Total={total_time:.2f}s"
        )

    return results


def print_statistics(results: dict):
    """Print profiling statistics."""
    print("\n" + "=" * 70)
    print("TIME PROFILING RESULTS (20 iterations)")
    print("=" * 70)
    print()

    components = [
        ("Phase 1 - Network", "phase1_network"),
        ("Phase 1 - Validation", "phase1_validation"),
        ("Phase 2 - Network", "phase2_network"),
        ("Phase 2 - Validation", "phase2_validation"),
    ]

    total_mean = statistics.mean(results["total"])

    print(f"{'Component':<25} {'Mean':<10} {'StdDev':<10} {'% of Total':<12}")
    print("-" * 70)

    for label, key in components:
        mean = statistics.mean(results[key])
        stdev = statistics.stdev(results[key]) if len(results[key]) > 1 else 0
        percentage = (mean / total_mean) * 100
        print(f"{label:<25} {mean:<10.3f} {stdev:<10.3f} {percentage:<12.1f}%")

    # Calculate overhead
    accounted_time = sum(statistics.mean(results[key]) for _, key in components)
    overhead = total_mean - accounted_time
    overhead_pct = (overhead / total_mean) * 100

    print(f"{'Other overhead':<25} {overhead:<10.3f} {'N/A':<10} {overhead_pct:<12.1f}%")
    print("-" * 70)
    print(f"{'TOTAL':<25} {total_mean:<10.3f} {statistics.stdev(results['total']):<10.3f} {'100.0':<12}%")
    print()

    # Insights
    print("=" * 70)
    print("INSIGHTS")
    print("=" * 70)
    print()

    network_total = statistics.mean(results["phase1_network"]) + statistics.mean(
        results["phase2_network"]
    )
    validation_total = statistics.mean(results["phase1_validation"]) + statistics.mean(
        results["phase2_validation"]
    )

    network_pct = (network_total / total_mean) * 100
    validation_pct = (validation_total / total_mean) * 100

    print(f"📡 Network I/O: {network_total:.3f}s ({network_pct:.1f}% of total)")
    print(
        f"✅ Pydantic Validation: {validation_total:.3f}s ({validation_pct:.1f}% of total)"
    )
    print(f"⚙️  Other (JSON parsing, overhead): {overhead:.3f}s ({overhead_pct:.1f}% of total)")
    print()

    # Recommendations
    print("=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print()

    if validation_pct > 10:
        print(
            f"⚠️  Validation is {validation_pct:.1f}% of total time - consider optimizations:"
        )
        print("   - Use model_validate() with strict=False")
        print("   - Consider model_construct() for trusted data (skips validation)")
        print("   - Batch validation in thread pool executor")
    else:
        print(
            f"✅ Validation is only {validation_pct:.1f}% of total time - already optimal"
        )

    print()

    if network_pct > 80:
        print(
            f"⚠️  Network I/O dominates at {network_pct:.1f}% - server is the bottleneck"
        )
        print("   - HTTP/2 multiplexing is already being used")
        print("   - Server-side processing time cannot be optimized from client")
        print("   - Consider requesting larger page sizes if API allows")
    else:
        print(f"✅ Network I/O at {network_pct:.1f}% is reasonable")

    print()
    print("=" * 70)


async def main():
    """Run profiling."""
    async with AsyncOFSC(
        clientID=Config.OFSC_CLIENT_ID,
        secret=Config.OFSC_CLIENT_SECRET,
        companyName=Config.OFSC_COMPANY,
        root=Config.OFSC_ROOT,
    ) as client:
        print("=" * 70)
        print("PROFILING PARALLEL PAGINATION PERFORMANCE")
        print("=" * 70)
        print(f"Connected to: {Config.OFSC_COMPANY}")
        print("HTTP/2 enabled: Yes")
        print("Iterations: 20")
        print()

        results = await profile_parallel_approach(client, iterations=20)
        print_statistics(results)


if __name__ == "__main__":
    asyncio.run(main())
