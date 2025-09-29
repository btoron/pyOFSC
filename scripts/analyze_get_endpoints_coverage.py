#!/usr/bin/env python3
"""
Analyze GET endpoints implementation vs saved response coverage.

This script compares implemented GET endpoints from ENDPOINTS.md with saved responses
in the response_examples directory to show coverage statistics and identify gaps.
"""

import re
import os
from pathlib import Path
from typing import List, Set
from dataclasses import dataclass


@dataclass
class EndpointInfo:
    """Represents an endpoint from ENDPOINTS.md"""

    id: int
    path: str
    method: str
    module: str
    implemented: bool
    signature: str


def parse_endpoints_md(file_path: str) -> List[EndpointInfo]:
    """Parse ENDPOINTS.md and extract endpoint information."""
    endpoints = []

    with open(file_path, "r") as f:
        content = f.read()

    # Find all table rows with endpoint data
    pattern = r"^\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|\s*(\w+)\s*\|\s*(\w+)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|"

    for line in content.split("\n"):
        match = re.match(pattern, line.strip())
        if match:
            endpoint_id = int(match.group(1))
            path = match.group(2)
            method = match.group(3).upper()
            module = match.group(4)
            implemented_in = match.group(5).strip()
            signature = match.group(6).strip()

            # Check if endpoint is implemented (has version number, not empty, not DEPRECATED)
            is_implemented = bool(
                implemented_in
                and implemented_in != ""
                and implemented_in.upper() != "DEPRECATED"
                and "v3.0.0-dev" in implemented_in
            )

            # Clean up signature - remove markdown backticks
            if signature.startswith("`") and signature.endswith("`"):
                signature = signature[1:-1]

            endpoints.append(
                EndpointInfo(
                    id=endpoint_id,
                    path=path,
                    method=method,
                    module=module,
                    implemented=is_implemented,
                    signature=signature,
                )
            )

    return endpoints


def get_saved_response_ids(response_dir: str) -> Set[int]:
    """Extract endpoint IDs from saved response filenames."""
    response_ids = set()

    if not os.path.exists(response_dir):
        return response_ids

    for filename in os.listdir(response_dir):
        # Look for files starting with number_
        match = re.match(r"^(\d+)_", filename)
        if match:
            response_ids.add(int(match.group(1)))

    return response_ids


def analyze_coverage():
    """Generate comprehensive coverage analysis."""

    print("=" * 80)
    print("🔍 GET ENDPOINTS IMPLEMENTATION vs SAVED RESPONSE COVERAGE ANALYSIS")
    print("=" * 80)
    print()

    # Parse endpoints
    endpoints_md_path = "docs/ENDPOINTS.md"
    if not Path(endpoints_md_path).exists():
        print(f"❌ Error: {endpoints_md_path} not found")
        return

    all_endpoints = parse_endpoints_md(endpoints_md_path)
    print(f"📋 Loaded {len(all_endpoints)} total endpoints from ENDPOINTS.md")

    # Filter GET endpoints only
    get_endpoints = [ep for ep in all_endpoints if ep.method == "GET"]
    print(f"🔗 Found {len(get_endpoints)} GET endpoints")

    # Filter implemented GET endpoints
    implemented_get_endpoints = [ep for ep in get_endpoints if ep.implemented]
    print(f"✅ Found {len(implemented_get_endpoints)} implemented GET endpoints")
    print()

    # Get saved response IDs
    response_dir = "response_examples"
    saved_response_ids = get_saved_response_ids(response_dir)
    print(f"💾 Found saved responses for {len(saved_response_ids)} endpoint IDs")
    print()

    # Cross-reference
    implemented_ids = {ep.id for ep in implemented_get_endpoints}
    with_responses = implemented_ids & saved_response_ids
    without_responses = implemented_ids - saved_response_ids

    coverage_percentage = (
        len(with_responses) / len(implemented_get_endpoints) * 100
        if implemented_get_endpoints
        else 0
    )

    # Statistics
    print("📊 COVERAGE STATISTICS")
    print("=" * 50)
    print(f"Total GET endpoints: {len(get_endpoints)}")
    print(
        f"Implemented GET endpoints: {len(implemented_get_endpoints)} ({len(implemented_get_endpoints) / len(get_endpoints) * 100:.1f}%)"
    )
    print(
        f"Implemented GET endpoints with saved responses: {len(with_responses)} ({coverage_percentage:.1f}%)"
    )
    print(
        f"Implemented GET endpoints missing saved responses: {len(without_responses)}"
    )
    print()

    # Breakdown by module
    modules = {}
    for ep in implemented_get_endpoints:
        if ep.module not in modules:
            modules[ep.module] = {"total": 0, "with_responses": 0}
        modules[ep.module]["total"] += 1
        if ep.id in saved_response_ids:
            modules[ep.module]["with_responses"] += 1

    print("📈 COVERAGE BY MODULE")
    print("=" * 50)
    for module, stats in sorted(modules.items()):
        coverage = (
            stats["with_responses"] / stats["total"] * 100 if stats["total"] > 0 else 0
        )
        status = "✅" if coverage > 70 else "⚠️" if coverage > 40 else "❌"
        print(
            f"{status} {module}: {stats['with_responses']}/{stats['total']} ({coverage:.1f}%)"
        )
    print()

    # Detailed listings
    print("✅ IMPLEMENTED GET ENDPOINTS WITH SAVED RESPONSES")
    print("=" * 60)

    endpoints_with_responses = [
        ep for ep in implemented_get_endpoints if ep.id in saved_response_ids
    ]
    endpoints_with_responses.sort(key=lambda x: x.id)

    for ep in endpoints_with_responses:
        # Find response files for this endpoint
        response_files = []
        for filename in (
            os.listdir(response_dir) if os.path.exists(response_dir) else []
        ):
            if filename.startswith(f"{ep.id}_"):
                response_files.append(filename)

        files_str = ", ".join(response_files) if response_files else "unknown"
        print(f"ID {ep.id:3d}: {ep.method} {ep.path}")
        print(f"       Module: {ep.module} | Files: {files_str}")
        print()

    print("❌ IMPLEMENTED GET ENDPOINTS MISSING SAVED RESPONSES")
    print("=" * 60)

    endpoints_without_responses = [
        ep for ep in implemented_get_endpoints if ep.id not in saved_response_ids
    ]
    endpoints_without_responses.sort(key=lambda x: x.id)

    for ep in endpoints_without_responses:
        print(f"ID {ep.id:3d}: {ep.method} {ep.path}")
        print(f"       Module: {ep.module}")
        if ep.signature:
            print(
                f"       Signature: {ep.signature[:80]}{'...' if len(ep.signature) > 80 else ''}"
            )
        print()

    # Recommendations
    print("🎯 RECOMMENDATIONS")
    print("=" * 50)

    if without_responses:
        print(f"Priority for response collection ({len(without_responses)} endpoints):")

        # Group by module for better organization
        by_module = {}
        for ep in endpoints_without_responses:
            if ep.module not in by_module:
                by_module[ep.module] = []
            by_module[ep.module].append(ep)

        for module, eps in sorted(by_module.items()):
            print(f"\n📦 {module.upper()} MODULE ({len(eps)} endpoints):")
            for ep in sorted(eps, key=lambda x: x.id):
                # Determine priority based on endpoint characteristics
                priority = (
                    "🔴 HIGH"
                    if any(
                        keyword in ep.path.lower()
                        for keyword in ["activities", "resources", "users"]
                    )
                    else "🟡 MED"
                    if any(
                        keyword in ep.path.lower()
                        for keyword in ["properties", "types", "categories"]
                    )
                    else "🟢 LOW"
                )
                print(f"   {priority} - ID {ep.id}: {ep.path}")
    else:
        print("🎉 Excellent! All implemented GET endpoints have saved responses.")

    print()
    print("=" * 80)
    print(
        f"Analysis complete. Coverage: {coverage_percentage:.1f}% ({len(with_responses)}/{len(implemented_get_endpoints)})"
    )
    print("=" * 80)


if __name__ == "__main__":
    analyze_coverage()
