#!/usr/bin/env python3
"""Parallel test execution script with category-specific parallelism controls.

This script provides intelligent parallel test execution that respects rate limits
and optimizes performance for different test categories.
"""

import os
import subprocess
import argparse
from pathlib import Path
from typing import List


def get_cpu_count() -> int:
    """Get the number of available CPU cores."""
    # Check for CI environment variable overrides
    if "PYTEST_WORKERS" in os.environ:
        try:
            return int(os.environ["PYTEST_WORKERS"])
        except ValueError:
            pass

    # Default to system CPU count
    return os.cpu_count() or 1


def determine_worker_count(test_category: str, total_cpus: int) -> int:
    """Determine optimal worker count for different test categories."""

    # Check for environment variable override
    disable_parallel = os.environ.get("PYTEST_DISABLE_PARALLEL", "").lower() in (
        "true",
        "1",
        "yes",
    )
    if disable_parallel:
        return 1

    # Category-specific worker limits
    worker_limits = {
        "unit": min(total_cpus, 8),  # CPU-bound, high parallelism
        "models": min(total_cpus, 8),  # CPU-bound, high parallelism
        "integration": min(total_cpus // 2, 4),  # Moderate parallelism
        "end_to_end": min(10, total_cpus),  # Rate-limited, max 10
        "live": min(10, total_cpus),  # Rate-limited, max 10
        "all": min(total_cpus // 2, 4),  # Conservative for mixed tests
    }

    return worker_limits.get(test_category, worker_limits["all"])


def build_pytest_command(
    test_paths: List[str],
    test_category: str,
    parallel: bool = True,
    additional_args: List[str] = None,
) -> List[str]:
    """Build pytest command with appropriate parallelism settings."""

    cmd = ["uv", "run", "pytest"]

    if parallel:
        cpu_count = get_cpu_count()
        worker_count = determine_worker_count(test_category, cpu_count)

        if worker_count > 1:
            cmd.extend(["-n", str(worker_count)])
            cmd.extend(["--dist", "worksteal"])

            # Add category-specific settings
            if test_category in ["end_to_end", "live"]:
                # Add retry for rate-limited tests
                cmd.extend(["--reruns", "2", "--reruns-delay", "5"])

                # Set environment variable for rate limiting
                os.environ["PYTEST_RATE_LIMITED"] = "true"

            print(f"Running {test_category} tests with {worker_count} workers")
        else:
            print(f"Running {test_category} tests sequentially (parallel disabled)")
    else:
        print(f"Running {test_category} tests sequentially")

    # Add test paths
    cmd.extend(test_paths)

    # Add verbose output
    cmd.extend(["-v"])

    # Add additional arguments
    if additional_args:
        cmd.extend(additional_args)

    return cmd


def run_test_category(
    category: str,
    paths: List[str],
    parallel: bool = True,
    additional_args: List[str] = None,
) -> subprocess.CompletedProcess:
    """Run tests for a specific category."""

    print(f"\n{'=' * 60}")
    print(f"Running {category.upper()} tests")
    print(f"{'=' * 60}")

    cmd = build_pytest_command(paths, category, parallel, additional_args)

    print(f"Command: {' '.join(cmd)}")
    print()

    # Set environment variables for this test run
    env = os.environ.copy()
    env["PYTEST_CURRENT_CATEGORY"] = category

    return subprocess.run(cmd, env=env)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Run tests with optimized parallel execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --all                    # Run all tests with category-optimized parallelism
  %(prog)s --unit                   # Run only unit tests
  %(prog)s --end-to-end            # Run only end-to-end tests
  %(prog)s --sequential            # Run all tests sequentially
  %(prog)s --unit --parallel       # Run unit tests in parallel (default)
  %(prog)s --custom tests/unit/    # Run custom test path
        """,
    )

    # Test category selection
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument(
        "--all", action="store_true", help="Run all tests (default)"
    )
    test_group.add_argument("--unit", action="store_true", help="Run unit tests only")
    test_group.add_argument(
        "--models", action="store_true", help="Run model tests only"
    )
    test_group.add_argument(
        "--integration", action="store_true", help="Run integration tests only"
    )
    test_group.add_argument(
        "--end-to-end", action="store_true", help="Run end-to-end tests only"
    )
    test_group.add_argument("--live", action="store_true", help="Run live tests only")
    test_group.add_argument("--custom", nargs="+", help="Run tests from custom paths")

    # Execution mode
    execution_group = parser.add_mutually_exclusive_group()
    execution_group.add_argument(
        "--parallel",
        action="store_true",
        default=True,
        help="Run tests in parallel (default)",
    )
    execution_group.add_argument(
        "--sequential", action="store_true", help="Run tests sequentially"
    )

    # Additional options
    parser.add_argument(
        "--workers",
        type=int,
        help="Number of parallel workers (overrides auto-detection)",
    )
    parser.add_argument(
        "--measure", action="store_true", help="Measure and report execution time"
    )
    parser.add_argument(
        "--pytest-args", nargs="*", help="Additional arguments to pass to pytest"
    )

    args = parser.parse_args()

    # Ensure we're in the project root
    if not Path("pyproject.toml").exists():
        print("Error: Must run from project root (where pyproject.toml exists)")
        return 1

    # Override worker count if specified
    if args.workers:
        os.environ["PYTEST_WORKERS"] = str(args.workers)

    # Determine execution mode
    parallel = args.parallel and not args.sequential

    # Determine test categories to run
    test_categories = []

    if args.unit:
        test_categories.append(("unit", ["tests/unit/"]))
    elif args.models:
        test_categories.append(("models", ["tests/models/"]))
    elif args.integration:
        test_categories.append(("integration", ["tests/integration/"]))
    elif args.end_to_end:
        test_categories.append(("end_to_end", ["tests/end_to_end/"]))
    elif args.live:
        test_categories.append(
            ("live", ["tests/live/", "tests/end_to_end/", "-m", "live"])
        )
    elif args.custom:
        test_categories.append(("custom", args.custom))
    else:
        # Default: run all tests in optimized order
        test_categories = [
            ("unit", ["tests/unit/"]),
            ("models", ["tests/models/"]),
            ("end_to_end", ["tests/end_to_end/"]),
        ]

    # Track overall results
    failed_categories = []
    total_start_time = None

    if args.measure:
        import time

        total_start_time = time.time()

    # Run each test category
    for category, paths in test_categories:
        result = run_test_category(category, paths, parallel, args.pytest_args)

        if result.returncode != 0:
            failed_categories.append(category)
            print(f"\n❌ {category.upper()} tests failed")
        else:
            print(f"\n✅ {category.upper()} tests passed")

    # Print summary
    if args.measure and total_start_time:
        total_time = time.time() - total_start_time
        print(f"\n{'=' * 60}")
        print("EXECUTION SUMMARY")
        print(f"{'=' * 60}")
        print(f"Total execution time: {total_time:.2f}s")
        print(f"Parallel execution: {'Yes' if parallel else 'No'}")
        if parallel:
            cpu_count = get_cpu_count()
            print(f"Available CPUs: {cpu_count}")

    if failed_categories:
        print(f"\n❌ Failed categories: {', '.join(failed_categories)}")
        return 1
    else:
        print("\n✅ All test categories passed")
        return 0


if __name__ == "__main__":
    exit(main())
