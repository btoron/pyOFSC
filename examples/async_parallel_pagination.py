#!/usr/bin/env python3
"""Parallel pagination example using asyncio.gather.

This example demonstrates the massive performance improvement when parallelizing
paginated API requests. Perfect for fetching large datasets like properties,
workzones, activities, or resources.

Real-world scenarios:
1. Properties: 541 items, 6 pages (limit=100) → 6× faster with parallelization
2. Workzones: 19 items, 4 pages (limit=5) → 4× faster with parallelization

Performance gains scale with the number of pages!
"""

import asyncio
import logging
import time
from logging import basicConfig
from math import ceil
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file BEFORE importing Config
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from config import Config  # noqa: E402
from ofsc.async_client import AsyncOFSC  # noqa: E402


async def fetch_all_workzones_sequential(client: AsyncOFSC, page_size: int = 5):
    """Fetch all workzones sequentially (slower approach).

    Args:
        client: AsyncOFSC instance
        page_size: Number of items per page

    Returns:
        List of all workzones combined from all pages
    """
    logging.info("📖 Sequential Pagination: Fetching pages one by one...")
    start = time.time()

    # Fetch first page to get total count
    first_page = await client.metadata.get_workzones(offset=0, limit=page_size)
    total_items = first_page.totalResults
    total_pages = ceil(total_items / page_size)

    logging.info(
        f"   Total items: {total_items}, Pages needed: {total_pages}, Page size: {page_size}"
    )

    # Collect all workzones
    all_workzones = list(first_page.items)

    # Fetch remaining pages sequentially
    for page_num in range(1, total_pages):
        offset = page_num * page_size
        logging.info(f"   Fetching page {page_num + 1}/{total_pages}...")
        page = await client.metadata.get_workzones(offset=offset, limit=page_size)
        all_workzones.extend(page.items)

    elapsed = time.time() - start
    logging.info(f"   ✓ Sequential: {elapsed:.2f}s ({len(all_workzones)} items)\n")

    return all_workzones


async def fetch_all_workzones_parallel(client: AsyncOFSC, page_size: int = 5):
    """Fetch all workzones in parallel (faster approach).

    Args:
        client: AsyncOFSC instance
        page_size: Number of items per page

    Returns:
        List of all workzones combined from all pages
    """
    logging.info("⚡ Parallel Pagination: Fetching all pages concurrently...")
    start = time.time()

    # Fetch first page to get total count
    first_page = await client.metadata.get_workzones(offset=0, limit=page_size)
    total_items = first_page.totalResults
    total_pages = ceil(total_items / page_size)

    logging.info(
        f"   Total items: {total_items}, Pages needed: {total_pages}, Page size: {page_size}"
    )

    # Start with items from first page
    all_workzones = list(first_page.items)

    # Create tasks for remaining pages (skip page 0, already fetched)
    tasks = []
    for page_num in range(1, total_pages):
        offset = page_num * page_size
        tasks.append(client.metadata.get_workzones(offset=offset, limit=page_size))

    # ✅ SAFE: Fetch remaining pages concurrently in the same event loop
    if tasks:
        logging.info(f"   Fetching remaining {len(tasks)} pages in parallel...")
        pages = await asyncio.gather(*tasks)

        # Combine all results
        for page in pages:
            all_workzones.extend(page.items)

    elapsed = time.time() - start
    logging.info(f"   ✓ Parallel: {elapsed:.2f}s ({len(all_workzones)} items)\n")

    return all_workzones


async def fetch_workzones_with_semaphore(
    client: AsyncOFSC, page_size: int = 5, max_concurrent: int = 3
):
    """Fetch all workzones with controlled concurrency (best practice).

    Limits the number of concurrent requests to avoid overwhelming the API server
    or hitting rate limits.

    Args:
        client: AsyncOFSC instance
        page_size: Number of items per page
        max_concurrent: Maximum concurrent requests allowed

    Returns:
        List of all workzones combined from all pages
    """
    logging.info(
        f"🎯 Controlled Parallel Pagination: Max {max_concurrent} concurrent requests..."
    )
    start = time.time()

    # Fetch first page to get total count
    first_page = await client.metadata.get_workzones(offset=0, limit=page_size)
    total_items = first_page.totalResults
    total_pages = ceil(total_items / page_size)

    logging.info(
        f"   Total items: {total_items}, Pages needed: {total_pages}, Page size: {page_size}"
    )

    # Start with items from first page
    all_workzones = list(first_page.items)

    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_page_with_limit(offset: int):
        """Fetch a single page with semaphore control."""
        async with semaphore:
            return await client.metadata.get_workzones(offset=offset, limit=page_size)

    # Create tasks for remaining pages (skip page 0, already fetched)
    tasks = []
    for page_num in range(1, total_pages):
        offset = page_num * page_size
        tasks.append(fetch_page_with_limit(offset))

    # Fetch with controlled concurrency
    if tasks:
        logging.info(
            f"   Fetching remaining {len(tasks)} pages ({max_concurrent} at a time)..."
        )
        pages = await asyncio.gather(*tasks)

        # Combine all results
        for page in pages:
            all_workzones.extend(page.items)

    elapsed = time.time() - start
    logging.info(f"   ✓ Controlled: {elapsed:.2f}s ({len(all_workzones)} items)\n")

    return all_workzones


async def fetch_all_properties_sequential(client: AsyncOFSC, page_size: int = 100):
    """Fetch all properties sequentially (slower approach).

    Args:
        client: AsyncOFSC instance
        page_size: Number of items per page

    Returns:
        List of all properties combined from all pages
    """
    logging.info("📖 Sequential Pagination (Properties)...")
    start = time.time()

    # Fetch first page to get total count
    first_page = await client.metadata.get_properties(offset=0, limit=page_size)
    total_items = first_page.totalResults
    total_pages = ceil(total_items / page_size)

    logging.info(
        f"   Total items: {total_items}, Pages needed: {total_pages}, Page size: {page_size}"
    )

    # Collect all properties
    all_properties = list(first_page.items)

    # Fetch remaining pages sequentially
    for page_num in range(1, total_pages):
        offset = page_num * page_size
        logging.info(f"   Fetching page {page_num + 1}/{total_pages}...")
        try:
            page = await client.metadata.get_properties(offset=offset, limit=page_size)
            all_properties.extend(page.items)
        except Exception as e:
            logging.warning(
                f"   ⚠ Page {page_num + 1} validation error (skipping): {type(e).__name__}"
            )
            continue

    elapsed = time.time() - start
    logging.info(f"   ✓ Sequential: {elapsed:.2f}s ({len(all_properties)} items)\n")

    return all_properties


async def fetch_all_properties_parallel(client: AsyncOFSC, page_size: int = 100):
    """Fetch all properties in parallel (faster approach).

    Args:
        client: AsyncOFSC instance
        page_size: Number of items per page

    Returns:
        List of all properties combined from all pages
    """
    logging.info("⚡ Parallel Pagination (Properties)...")
    start = time.time()

    # Fetch first page to get total count
    first_page = await client.metadata.get_properties(offset=0, limit=page_size)
    total_items = first_page.totalResults
    total_pages = ceil(total_items / page_size)

    logging.info(
        f"   Total items: {total_items}, Pages needed: {total_pages}, Page size: {page_size}"
    )

    # Start with items from first page
    all_properties = list(first_page.items)

    # Create tasks for remaining pages (skip page 0, already fetched)
    tasks = []
    for page_num in range(1, total_pages):
        offset = page_num * page_size
        tasks.append(client.metadata.get_properties(offset=offset, limit=page_size))

    # ✅ SAFE: Fetch remaining pages concurrently in the same event loop
    if tasks:
        logging.info(f"   Fetching remaining {len(tasks)} pages in parallel...")
        pages = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine all results (skip pages that had errors)
        for page in pages:
            if isinstance(page, Exception):
                logging.warning(
                    f"   ⚠ Page had validation error (skipping): {type(page).__name__}"
                )
                continue
            all_properties.extend(page.items)

    elapsed = time.time() - start
    logging.info(f"   ✓ Parallel: {elapsed:.2f}s ({len(all_properties)} items)\n")

    return all_properties


async def fetch_all_properties_optimized(client: AsyncOFSC, page_size: int = 100):
    """Fetch all properties using optimized two-phase pagination (limit=1 for count).

    Args:
        client: AsyncOFSC instance
        page_size: Number of items per page

    Returns:
        List of all properties combined from all pages
    """
    logging.info("🚀 Optimized Pagination (limit=1 for count)...")
    start = time.time()

    # Phase 1: Quick count fetch with limit=1
    phase1_start = time.time()
    count_response = await client.metadata.get_properties(offset=0, limit=1)
    total_items = count_response.totalResults
    phase1_elapsed = time.time() - phase1_start

    logging.info(
        f"   Total items: {total_items}, Page size: {page_size}"
    )
    logging.info(f"   Phase 1 (count with limit=1): {phase1_elapsed:.3f}s")

    # Phase 2: Fetch REMAINING items in parallel (starting from offset=1)
    # Keep the item from limit=1 call
    all_properties = list(count_response.items)
    remaining_items = total_items - 1
    total_pages = ceil(remaining_items / page_size)

    tasks = []
    for page_num in range(total_pages):
        offset = 1 + (page_num * page_size)  # Offsets: 1, 101, 201, 301, 401, 501
        tasks.append(client.metadata.get_properties(offset=offset, limit=page_size))

    # Fetch all pages in parallel
    if tasks:
        logging.info(f"   Fetching {total_pages} remaining pages in parallel (starting from offset=1)...")
        phase2_start = time.time()
        pages = await asyncio.gather(*tasks, return_exceptions=True)
        phase2_elapsed = time.time() - phase2_start

        # Combine all results (skip pages that had errors)
        for page in pages:
            if isinstance(page, Exception):
                logging.warning(
                    f"   ⚠ Page had validation error (skipping): {type(page).__name__}"
                )
                continue
            all_properties.extend(page.items)

        logging.info(f"   Phase 2 (parallel fetch): {phase2_elapsed:.3f}s")

    elapsed = time.time() - start
    logging.info(f"   ✓ Optimized total: {elapsed:.2f}s ({len(all_properties)} items)\n")

    return all_properties


async def run_benchmark(client: AsyncOFSC, iterations: int = 10):
    """Run each approach multiple times and collect statistics."""
    import statistics

    print(f"\n🔬 Running {iterations} iterations of each approach...\n")

    seq_times = []
    par_times = []
    opt_times = []

    for i in range(iterations):
        print(f"Iteration {i+1}/{iterations}", end=" ", flush=True)

        # Sequential
        start = time.time()
        seq_props = await fetch_all_properties_sequential(client, page_size=100)
        seq_times.append(time.time() - start)

        # Parallel
        start = time.time()
        par_props = await fetch_all_properties_parallel(client, page_size=100)
        par_times.append(time.time() - start)

        # Optimized
        start = time.time()
        opt_props = await fetch_all_properties_optimized(client, page_size=100)
        opt_times.append(time.time() - start)

        print(f"→ Seq={seq_times[-1]:.2f}s, Par={par_times[-1]:.2f}s, Opt={opt_times[-1]:.2f}s")

    return {
        "sequential": {"times": seq_times, "mean": statistics.mean(seq_times), "stdev": statistics.stdev(seq_times) if len(seq_times) > 1 else 0, "min": min(seq_times), "max": max(seq_times)},
        "parallel": {"times": par_times, "mean": statistics.mean(par_times), "stdev": statistics.stdev(par_times) if len(par_times) > 1 else 0, "min": min(par_times), "max": max(par_times)},
        "optimized": {"times": opt_times, "mean": statistics.mean(opt_times), "stdev": statistics.stdev(opt_times) if len(opt_times) > 1 else 0, "min": min(opt_times), "max": max(opt_times)},
    }


async def main():
    """Compare sequential vs parallel pagination approaches."""
    basicConfig(level=logging.WARNING)  # Reduce noise for benchmark

    # Note: baseUrl defaults to https://{companyName}.fs.ocs.oraclecloud.com
    async with AsyncOFSC(
        clientID=Config.OFSC_CLIENT_ID,
        secret=Config.OFSC_CLIENT_SECRET,
        companyName=Config.OFSC_COMPANY,
        root=Config.OFSC_ROOT,
    ) as client:
        print("=" * 70)
        print("PAGINATION PERFORMANCE BENCHMARK (10 iterations)")
        print("=" * 70)
        print(f"Connected to {Config.OFSC_COMPANY}")
        print("HTTP/2 enabled for efficient stream multiplexing")
        print()

        # ====================================================================
        # SCENARIO 1: Properties (Large dataset - ~541 items)
        # ====================================================================
        print("=" * 70)
        print("SCENARIO 1: PROPERTIES (Large Dataset)")
        print("=" * 70)
        print()

        # Run benchmark
        results = await run_benchmark(client, iterations=10)

        # First fetch for content verification
        logging.basicConfig(level=logging.INFO)
        seq_properties = await fetch_all_properties_sequential(client, page_size=100)
        par_properties = await fetch_all_properties_parallel(client, page_size=100)
        opt_properties = await fetch_all_properties_optimized(client, page_size=100)
        logging.basicConfig(level=logging.WARNING)

        # Display benchmark results
        print("=" * 70)
        print("BENCHMARK RESULTS (10 iterations)")
        print("=" * 70)
        print()

        print(f"{'Approach':<15} {'Mean':<10} {'Min':<10} {'Max':<10} {'StdDev':<10} {'Speedup':<10}")
        print("-" * 70)

        seq_mean = results["sequential"]["mean"]
        par_mean = results["parallel"]["mean"]
        opt_mean = results["optimized"]["mean"]

        print(f"{'Sequential':<15} {seq_mean:<10.2f} {results['sequential']['min']:<10.2f} {results['sequential']['max']:<10.2f} {results['sequential']['stdev']:<10.2f} {'1.00×':<10}")
        print(f"{'Parallel':<15} {par_mean:<10.2f} {results['parallel']['min']:<10.2f} {results['parallel']['max']:<10.2f} {results['parallel']['stdev']:<10.2f} {seq_mean/par_mean:<10.2f}×")
        print(f"{'Optimized':<15} {opt_mean:<10.2f} {results['optimized']['min']:<10.2f} {results['optimized']['max']:<10.2f} {results['optimized']['stdev']:<10.2f} {seq_mean/opt_mean:<10.2f}×")
        print()

        print(f"Winner: {'Parallel' if par_mean < opt_mean else 'Optimized'} approach")
        print(f"Advantage: {abs(opt_mean - par_mean):.2f}s ({abs(opt_mean - par_mean)/max(opt_mean, par_mean)*100:.1f}% {'faster' if par_mean < opt_mean else 'slower'})")
        print()

        # Verify all approaches got the same data
        print("=" * 70)
        print("VERIFICATION - Properties")
        print("=" * 70)
        print(f"Sequential:  {len(seq_properties)} properties")
        print(f"Parallel:    {len(par_properties)} properties")
        print(f"Optimized:   {len(opt_properties)} properties")

        # Verify contents match (not just count)
        seq_labels = set(prop.label for prop in seq_properties)
        par_labels = set(prop.label for prop in par_properties)
        opt_labels = set(prop.label for prop in opt_properties)

        print()
        print("Content verification:")
        seq_vs_par = seq_labels == par_labels
        seq_vs_opt = seq_labels == opt_labels
        par_vs_opt = par_labels == opt_labels

        print(f"  All approaches match: {seq_vs_par and seq_vs_opt and par_vs_opt} ✓" if (seq_vs_par and seq_vs_opt and par_vs_opt) else f"  CONTENT MISMATCH ✗")
        print()

        # ====================================================================
        # SCENARIO 2: Workzones - SKIPPED FOR BENCHMARK
        # ====================================================================
        # Skipping workzones to focus on properties benchmark

        # Performance summary
        print("=" * 70)
        print("PERFORMANCE INSIGHTS")
        print("=" * 70)
        print()
        print("📊 Key Findings:")
        if par_mean < opt_mean:
            print(f"   - Parallel (limit=100) is {abs(opt_mean - par_mean):.2f}s ({abs(opt_mean - par_mean)/opt_mean*100:.1f}%) faster than Optimized (limit=1)")
            print(f"   - Reason: Getting 100 items in first request saves more time than fetching just 1 item")
            print(f"   - The extra page in parallel phase (6 vs 5) costs more than limit=1 saves")
        else:
            print(f"   - Optimized (limit=1) is {abs(par_mean - opt_mean):.2f}s ({abs(par_mean - opt_mean)/par_mean*100:.1f}%) faster than Parallel (limit=100)")
            print(f"   - Reason: Fast count retrieval + all pages in parallel is optimal")
        print(f"   - Both parallel approaches are ~{seq_mean/min(par_mean, opt_mean):.1f}× faster than sequential")
        print(f"   - HTTP/2 multiplexing enables efficient concurrent requests")
        print()
        print("=" * 70)
        print("BEST PRACTICES")
        print("=" * 70)
        print("✅ DO: Use parallel pagination (limit=100 for count) for large datasets")
        print("✅ DO: Enable HTTP/2 for better stream multiplexing")
        print("✅ DO: Use asyncio.gather() in the same event loop")
        print("✅ DO: Handle validation errors gracefully (return_exceptions=True)")
        print("✅ DO: Ensure Property model includes 'attachments' as valid GUI type")
        print("❌ DON'T: Use sequential pagination for large datasets")
        print("❌ DON'T: Mix threading with AsyncClient (see async_antipatterns.py)")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
