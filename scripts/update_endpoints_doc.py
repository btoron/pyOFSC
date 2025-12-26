#!/usr/bin/env python3
"""Regenerate ENDPOINTS.md with current implementation status.

This script parses the Python source files to detect implemented endpoints
and updates the docs/ENDPOINTS.md file with current implementation status.
"""

import argparse
import re
import sys
import tomllib
from collections import defaultdict
from datetime import date
from pathlib import Path

# Constants
PROJECT_ROOT = Path(__file__).parent.parent
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
ENDPOINTS_PATH = PROJECT_ROOT / "docs" / "ENDPOINTS.md"

MODULE_FILE_MAP = {
    "core": ("ofsc/core.py", "ofsc/async_client/core.py"),
    "metadata": ("ofsc/metadata.py", "ofsc/async_client/metadata.py"),
    "capacity": ("ofsc/capacity.py", "ofsc/async_client/capacity.py"),
    "auth": ("ofsc/oauth.py", "ofsc/async_client/oauth.py"),
    # These modules have no implementation files
    "statistics": (None, None),
    "partscatalog": (None, None),
    "collaboration": (None, None),
}


def get_version_from_pyproject() -> str:
    """Read version from pyproject.toml."""
    with open(PYPROJECT_PATH, "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


def get_version_from_endpoints() -> str | None:
    """Extract version from ENDPOINTS.md metadata."""
    if not ENDPOINTS_PATH.exists():
        return None

    with open(ENDPOINTS_PATH) as f:
        for line in f:
            if line.startswith("**Version:**"):
                return line.split("**Version:**")[1].strip()
    return None


def parse_endpoints_md() -> list[dict]:
    """Parse existing ENDPOINTS.md to get endpoint list."""
    endpoints = []
    in_table = False

    with open(ENDPOINTS_PATH) as f:
        for line in f:
            line = line.strip()

            # Detect table start
            if line.startswith("| ID | Endpoint | Module | Method | Status |"):
                continue
            if line.startswith("|----"):
                in_table = True
                continue

            # End of table
            if in_table and (not line.startswith("|") or line.startswith("##")):
                break

            # Skip non-table lines
            if not in_table or not line.startswith("|"):
                continue

            # Parse table row
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 6:
                continue

            try:
                endpoint_id = parts[1]
                path = parts[2].strip("`")
                module = parts[3]
                method = parts[4]
                # Ignore current status - we'll recalculate it

                # Skip if not a valid endpoint ID
                if not endpoint_id.isdigit():
                    continue

                endpoints.append(
                    {
                        "id": int(endpoint_id),
                        "path": path,
                        "module": module,
                        "method": method,
                    }
                )
            except (IndexError, ValueError):
                continue

    return endpoints


def normalize_path_for_matching(path: str) -> str:
    """
    Normalize endpoint path for pattern matching.

    Converts path parameters like {activityId} to regex patterns.
    """
    # Escape regex special characters except {}
    escaped = re.escape(path)
    # Convert {param} to a pattern that matches any {word}
    pattern = escaped.replace(r"\{", "{").replace(r"\}", "}")
    return pattern


def scan_file_for_endpoints(file_path: Path) -> dict[tuple[str, str], bool]:
    """
    Scan a Python file for implemented endpoints.

    Returns:
        dict: Maps (path, method) -> is_implemented
              For async files, is_implemented = False if NotImplementedError
    """
    if not file_path.exists():
        return {}

    with open(file_path) as f:
        content = f.read()

    endpoints = {}
    is_async = "async_client" in str(file_path)

    # Pattern to find URL construction: urljoin(..., "PATH") or urljoin(..., f"PATH")
    # Also match .format() patterns like "/path/{}".format(var)
    # Match both regular strings and f-strings
    # For f-strings, replace {variable} with {}

    # Pattern 1: urljoin with direct string or f-string (single or multi-line)
    url_pattern = (
        r'urljoin\([^,]+,\s*f?["\']([^"\']+)["\']\s*(?:f?["\']([^"\']*)["\'])?'
    )
    raw_urls_from_urljoin = re.findall(url_pattern, content, re.MULTILINE)

    # Pattern 2: ".format() patterns
    format_pattern = r'["\']([^"\']*\/rest\/[^"\']+)["\']\.format\('
    raw_urls_from_format = re.findall(format_pattern, content)

    # Normalize f-string variables to {} and handle multi-line f-strings
    urls = []

    # Handle urljoin URLs (might be tuples from multi-line f-strings)
    for match in raw_urls_from_urljoin:
        if isinstance(match, tuple):
            # Multi-line f-string: concatenate parts
            url = "".join(part for part in match if part)
        else:
            url = match
        # Replace {variable} with {} for f-string paths
        normalized = re.sub(r"\{[^}]+\}", "{}", url)
        # Remove query parameters from URL
        normalized = re.sub(r"\?[^/]*$", "", normalized)
        # Remove trailing slash if present (to match ENDPOINTS.md convention)
        normalized = normalized.rstrip("/")
        urls.append(normalized)

    # Handle .format() URLs (already have {} placeholders)
    for url in raw_urls_from_format:
        # Remove query parameters
        normalized = re.sub(r"\?[^/]*$", "", url)
        # Remove trailing slash
        normalized = normalized.rstrip("/")
        urls.append(normalized)

    # For each URL found, try to find the HTTP method
    for url in urls:
        if not url.startswith("/rest/"):
            continue

        # Find the function/method containing this URL
        # Strategy: Find any urljoin that contains this URL (even partial), then check HTTP method
        # This handles multi-line f-strings, .format(), and other variations

        # Split URL into parts to handle multi-line f-strings
        # For multi-line f-strings like:
        #   f"/part1/{var1}/"
        #   f"{var2}/part2"
        # We need to find urljoin that might contain either part

        # Find all urljoin calls in the file and check which ones match this URL
        # Strategy: Find lines containing this URL (or parts of it for multi-line f-strings)
        # Then find the nearest urljoin above it

        urljoin_matches = []

        # Find all occurrences of "url = urljoin"
        all_urljoin = list(re.finditer(r"url\s*=\s*urljoin\s*\(", content))

        for urljoin_start in all_urljoin:
            # Get the code chunk from urljoin to the likely end (next 5 lines or 500 chars)
            start_pos = urljoin_start.start()
            end_search = min(len(content), start_pos + 500)

            # Find the matching closing paren
            paren_count = 0
            in_urljoin = False
            end_pos = start_pos

            for i in range(start_pos, end_search):
                if content[i] == "(":
                    paren_count += 1
                    in_urljoin = True
                elif content[i] == ")" and in_urljoin:
                    paren_count -= 1
                    if paren_count == 0:
                        end_pos = i + 1
                        break

            urljoin_chunk = content[start_pos:end_pos]

            # Extract URLs from this chunk
            chunk_url_parts = re.findall(r'f?["\']([^"\']+)["\']', urljoin_chunk)
            if chunk_url_parts:
                reconstructed = "".join(chunk_url_parts)
                reconstructed_normalized = re.sub(r"\{[^}]+\}", "{}", reconstructed)
                reconstructed_normalized = re.sub(
                    r"\?[^/]*$", "", reconstructed_normalized
                ).rstrip("/")

                if reconstructed_normalized == url:
                    # Create a match object-like structure
                    class FakeMatch:
                        def __init__(self, start, end):
                            self._start = start
                            self._end = end

                        def start(self):
                            return self._start

                        def end(self):
                            return self._end

                        def group(self):
                            return content[self._start : self._end]

                    urljoin_matches.append(FakeMatch(start_pos, end_pos))

        for urljoin_match in urljoin_matches:
            # Look ahead from urljoin to find the HTTP method (within next 1500 chars)
            # Some functions have long parameter processing before the HTTP call
            start_pos = urljoin_match.end()
            search_chunk = content[start_pos : start_pos + 1500]

            # Patterns to find HTTP method calls
            # Find the FIRST HTTP method call in the chunk
            # (the chunk might contain multiple functions, we want the first one)
            method_patterns = [
                (r"requests\.get\s*\(", "GET"),
                (r"requests\.post\s*\(", "POST"),
                (r"requests\.put\s*\(", "PUT"),
                (r"requests\.patch\s*\(", "PATCH"),
                (r"requests\.delete\s*\(", "DELETE"),
                (r"self\._client\.get\s*\(", "GET"),
                (r"self\._client\.post\s*\(", "POST"),
                (r"self\._client\.put\s*\(", "PUT"),
                (r"self\._client\.patch\s*\(", "PATCH"),
                (r"self\._client\.delete\s*\(", "DELETE"),
            ]

            # Find all matches and take the one that appears first
            http_method = None
            first_pos = float("inf")
            for pattern, method in method_patterns:
                match = re.search(pattern, search_chunk)
                if match and match.start() < first_pos:
                    first_pos = match.start()
                    http_method = method

            if http_method:
                # Check if this is a stub (async only)
                is_implemented = True
                if is_async:
                    # Check if NotImplementedError appears between function start and urljoin
                    # Find the function containing this URL
                    before_urljoin = content[: urljoin_match.start()]
                    func_matches = list(re.finditer(r"async def \w+", before_urljoin))
                    if func_matches:
                        last_func_match = func_matches[-1]
                        # Check content between function start and urljoin
                        func_to_urljoin = content[
                            last_func_match.end() : urljoin_match.start()
                        ]
                        if "raise NotImplementedError" in func_to_urljoin:
                            is_implemented = False

                # Store this endpoint (don't break - there may be multiple methods for same URL)
                endpoints[(url, http_method)] = is_implemented

    return endpoints


def build_implementation_map() -> dict[str, dict]:
    """
    Build a map of implementation status for all modules.

    Returns:
        dict: {module_name: {"sync": set((path, method)), "async": set((path, method))}}
    """
    impl_map = defaultdict(lambda: {"sync": {}, "async": {}})

    for module, (sync_file, async_file) in MODULE_FILE_MAP.items():
        # Scan sync file
        if sync_file:
            sync_path = PROJECT_ROOT / sync_file
            sync_endpoints = scan_file_for_endpoints(sync_path)
            impl_map[module]["sync"] = {k for k, v in sync_endpoints.items() if v}
            print(f"  - {sync_file}: {len(impl_map[module]['sync'])} endpoints found")

        # Scan async file
        if async_file:
            async_path = PROJECT_ROOT / async_file
            async_endpoints = scan_file_for_endpoints(async_path)
            impl_map[module]["async"] = {k for k, v in async_endpoints.items() if v}
            stubs = len([v for v in async_endpoints.values() if not v])
            print(
                f"  - {async_file}: {len(impl_map[module]['async'])} endpoints found "
                f"({stubs} stubs)"
            )

    return impl_map


def normalize_path_for_comparison(path: str) -> str:
    """
    Normalize path for comparison by replacing named params with {}.

    Examples:
        /rest/ofscCore/v1/activities/{activityId} -> /rest/ofscCore/v1/activities/{}
        /rest/ofscMetadata/v1/properties/{label} -> /rest/ofscMetadata/v1/properties/{}
    """
    # Replace {anything} with {}
    return re.sub(r"\{[^}]+\}", "{}", path)


def determine_status(endpoint: dict, impl_map: dict) -> str:
    """
    Determine implementation status for an endpoint.

    Args:
        endpoint: Endpoint dict with path, module, method
        impl_map: Implementation map from build_implementation_map()

    Returns:
        str: 'both', 'sync', 'async', or '-'
    """
    module = endpoint["module"]
    path = endpoint["path"]
    method = endpoint["method"]

    # Normalize path for comparison
    normalized_path = normalize_path_for_comparison(path)

    # Get implementation sets for this module
    module_impl = impl_map.get(module, {"sync": set(), "async": set()})

    # Check both exact match and normalized match
    sync_implemented = (path, method) in module_impl["sync"] or (
        normalized_path,
        method,
    ) in module_impl["sync"]
    async_implemented = (path, method) in module_impl["async"] or (
        normalized_path,
        method,
    ) in module_impl["async"]

    if sync_implemented and async_implemented:
        return "both"
    elif sync_implemented:
        return "sync"
    elif async_implemented:
        return "async"
    else:
        return "-"


def categorize_method(method: str) -> str:
    """Categorize HTTP method into GET, Write, DELETE."""
    if method == "GET":
        return "GET"
    elif method in ["POST", "PUT", "PATCH"]:
        return "Write"
    elif method == "DELETE":
        return "DELETE"
    else:
        return "Other"


def format_cell(implemented: int, total: int) -> str:
    """Format a table cell with count and percentage."""
    if total == 0:
        return "0/0 (0%)"
    percentage = round((implemented / total) * 100, 1)
    return f"{implemented}/{total} ({percentage}%)"


def generate_summary_tables(endpoints: list[dict]) -> str:
    """Generate summary statistics tables."""

    # Calculate statistics for sync and async
    def calc_stats(impl_type):
        stats = defaultdict(lambda: defaultdict(lambda: {"total": 0, "implemented": 0}))

        for ep in endpoints:
            module = ep["module"]
            method_cat = categorize_method(ep["method"])
            status = ep["status"]

            stats[module][method_cat]["total"] += 1

            if impl_type == "sync" and status in ["sync", "both"]:
                stats[module][method_cat]["implemented"] += 1
            elif impl_type == "async" and status in ["async", "both"]:
                stats[module][method_cat]["implemented"] += 1

        return stats

    sync_stats = calc_stats("sync")
    async_stats = calc_stats("async")

    # Generate tables
    all_modules = [
        "metadata",
        "core",
        "capacity",
        "statistics",
        "partscatalog",
        "collaboration",
        "auth",
    ]
    method_cats = ["GET", "Write", "DELETE"]

    lines = [
        "",
        "## Implementation Statistics by Module and Method",
        "",
    ]

    # Sync table
    lines.extend(
        [
            "### Synchronous Client",
            "",
            "| Module | GET | Write (POST/PUT/PATCH) | DELETE | Total |",
            "|:-------|----:|-----------------------:|-------:|------:|",
        ]
    )

    col_totals_sync = {cat: {"total": 0, "implemented": 0} for cat in method_cats}
    grand_total_sync = {"total": 0, "implemented": 0}

    for module in all_modules:
        row_total = {"total": 0, "implemented": 0}
        cells = [module]

        for method_cat in method_cats:
            data = sync_stats[module][method_cat]
            cells.append(format_cell(data["implemented"], data["total"]))
            row_total["total"] += data["total"]
            row_total["implemented"] += data["implemented"]
            col_totals_sync[method_cat]["total"] += data["total"]
            col_totals_sync[method_cat]["implemented"] += data["implemented"]
            grand_total_sync["total"] += data["total"]
            grand_total_sync["implemented"] += data["implemented"]

        cells.append(format_cell(row_total["implemented"], row_total["total"]))
        lines.append("| " + " | ".join(cells) + " |")

    # Totals row for sync
    total_cells = ["**Total**"]
    for method_cat in method_cats:
        data = col_totals_sync[method_cat]
        total_cells.append(f"**{format_cell(data['implemented'], data['total'])}**")
    total_cells.append(
        f"**{format_cell(grand_total_sync['implemented'], grand_total_sync['total'])}**"
    )
    lines.append("| " + " | ".join(total_cells) + " |")

    lines.append("")

    # Async table
    lines.extend(
        [
            "### Asynchronous Client",
            "",
            "| Module | GET | Write (POST/PUT/PATCH) | DELETE | Total |",
            "|:-------|----:|-----------------------:|-------:|------:|",
        ]
    )

    col_totals_async = {cat: {"total": 0, "implemented": 0} for cat in method_cats}
    grand_total_async = {"total": 0, "implemented": 0}

    for module in all_modules:
        row_total = {"total": 0, "implemented": 0}
        cells = [module]

        for method_cat in method_cats:
            data = async_stats[module][method_cat]
            cells.append(format_cell(data["implemented"], data["total"]))
            row_total["total"] += data["total"]
            row_total["implemented"] += data["implemented"]
            col_totals_async[method_cat]["total"] += data["total"]
            col_totals_async[method_cat]["implemented"] += data["implemented"]
            grand_total_async["total"] += data["total"]
            grand_total_async["implemented"] += data["implemented"]

        cells.append(format_cell(row_total["implemented"], row_total["total"]))
        lines.append("| " + " | ".join(cells) + " |")

    # Totals row for async
    total_cells = ["**Total**"]
    for method_cat in method_cats:
        data = col_totals_async[method_cat]
        total_cells.append(f"**{format_cell(data['implemented'], data['total'])}**")
    total_cells.append(
        f"**{format_cell(grand_total_async['implemented'], grand_total_async['total'])}**"
    )
    lines.append("| " + " | ".join(total_cells) + " |")

    return "\n".join(lines)


def write_endpoints_md(endpoints: list[dict], version: str) -> None:
    """Write updated ENDPOINTS.md with new status and metadata."""
    today = date.today().isoformat()

    # Calculate statistics for header
    sync_count = sum(1 for ep in endpoints if ep["status"] in ["sync", "both"])
    async_count = sum(1 for ep in endpoints if ep["status"] in ["async", "both"])
    both_count = sum(1 for ep in endpoints if ep["status"] == "both")
    not_impl = sum(1 for ep in endpoints if ep["status"] == "-")

    # Build the document
    lines = [
        "# OFSC API Endpoints Reference",
        "",
        f"**Version:** {version}",
        f"**Last Updated:** {today}",
        "",
        "This document provides a comprehensive reference of all Oracle Field Service Cloud (OFSC) API endpoints and their implementation status in pyOFSC.",
        "",
        f"**Total Endpoints:** {len(endpoints)}",
        "",
        "## Implementation Status",
        "",
        "- `sync` - Implemented in synchronous client only",
        "- `async` - Implemented in asynchronous client only",
        "- `both` - Implemented in both sync and async clients",
        "- `-` - Not implemented",
        "",
        "## Endpoints Table",
        "",
        "| ID | Endpoint | Module | Method | Status |",
        "|----|----------|--------|--------|--------|",
    ]

    # Add endpoint rows
    for ep in endpoints:
        lines.append(
            f"| {ep['id']} | `{ep['path']}` | {ep['module']} | {ep['method']} | {ep['status']} |"
        )

    # Add implementation summary
    lines.extend(
        [
            "",
            "",
            "",
            "## Implementation Summary",
            "",
            f"- **Sync only**: {sync_count - both_count} endpoints",
            f"- **Async only**: {async_count - both_count} endpoints",
            f"- **Both**: {both_count} endpoints",
            f"- **Not implemented**: {not_impl} endpoints",
            f"- **Total sync**: {sync_count} endpoints",
            f"- **Total async**: {async_count} endpoints",
        ]
    )

    # Add summary tables
    lines.append(generate_summary_tables(endpoints))

    # Write file
    with open(ENDPOINTS_PATH, "w") as f:
        f.write("\n".join(lines))
        f.write("\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Update ENDPOINTS.md with current implementation status"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration even if version is unchanged",
    )
    args = parser.parse_args()

    # Get versions
    new_version = get_version_from_pyproject()
    current_version = get_version_from_endpoints()

    # Check if update is needed
    if current_version == new_version and not args.force:
        print(
            f"Version unchanged ({new_version}), skipping update. Use --force to regenerate."
        )
        return 0

    if current_version != new_version:
        print(f"Version changed from {current_version} to {new_version}")
    else:
        print(f"Force regeneration (version {new_version})")

    # Parse existing endpoints
    print("Parsing existing ENDPOINTS.md...")
    endpoints = parse_endpoints_md()
    print(f"Found {len(endpoints)} endpoints")

    # Build implementation map
    print("Scanning implementation files...")
    impl_map = build_implementation_map()

    # Update status for each endpoint
    print("Updating endpoint statuses...")
    for endpoint in endpoints:
        new_status = determine_status(endpoint, impl_map)
        endpoint["status"] = new_status

    # Write updated file
    print("Regenerating ENDPOINTS.md...")
    write_endpoints_md(endpoints, new_version)

    print(
        f"✓ Updated docs/ENDPOINTS.md (version {new_version}, {date.today().isoformat()})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
