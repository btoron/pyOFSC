#!/usr/bin/env python3
"""Regenerate ENDPOINTS.md with current implementation status.

This script parses the Python source files to detect implemented endpoints
and updates the docs/ENDPOINTS.md file with current implementation status.
"""

import argparse
import ast
import re
import sys
import tomllib
from collections import defaultdict
from datetime import date
from pathlib import Path

import io

from pytablewriter import MarkdownTableWriter

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


def dict_list_to_markdown_table(data: list[dict]) -> str:
    """Convert list of dictionaries to GitHub-flavored markdown table.

    Args:
        data: List of dictionaries where keys are column headers

    Returns:
        Markdown table string
    """
    if not data:
        return ""

    # Extract headers from first row
    headers = list(data[0].keys())

    # Build value matrix
    value_matrix = [[row[header] for header in headers] for row in data]

    # Create table using pytablewriter
    writer = MarkdownTableWriter(
        headers=headers, value_matrix=value_matrix, flavor="github"
    )

    # Capture output
    output = io.StringIO()
    writer.stream = output
    writer.write_table()

    return output.getvalue().strip()


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

                # Skip if not a valid endpoint ID (format: XXYYYM)
                if not re.match(r"^[A-Z]{2}\d{3}[GPUAD]$", endpoint_id):
                    continue

                endpoints.append(
                    {
                        "id": endpoint_id,  # Keep as string
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


def _extract_url_from_ast_node(node: ast.expr) -> str | None:
    """
    Extract URL string from AST node (Constant or JoinedStr).

    Args:
        node: AST expression node containing URL

    Returns:
        Normalized URL string with {variables} as {}, or None if not extractable
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        # Simple string: "/rest/ofscCore/v1/activities"
        return node.value

    elif isinstance(node, ast.JoinedStr):
        # F-string: f"/rest/ofscCore/v1/activities/{activity_id}"
        parts = []
        for value in node.values:
            if isinstance(value, ast.Constant):
                parts.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                # Replace variable with placeholder
                parts.append("{}")
        return "".join(parts)

    return None


def _get_http_method_from_call(node: ast.Call) -> str | None:
    """
    Determine HTTP method from a requests or httpx client call.

    Args:
        node: ast.Call node

    Returns:
        HTTP method string (GET, POST, etc.) or None
    """
    func = node.func

    # Pattern: requests.get(), requests.post(), self._client.get(), etc.
    if isinstance(func, ast.Attribute):
        attr_name = func.attr
        method_map = {
            "get": "GET",
            "post": "POST",
            "put": "PUT",
            "patch": "PATCH",
            "delete": "DELETE",
        }
        return method_map.get(attr_name)

    return None


def _function_raises_not_implemented(
    func_node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> bool:
    """
    Check if a function raises NotImplementedError.

    Args:
        func_node: Function definition node

    Returns:
        True if function raises NotImplementedError
    """
    for node in ast.walk(func_node):
        if isinstance(node, ast.Raise):
            # Check if raising NotImplementedError
            if node.exc and isinstance(node.exc, ast.Name):
                if node.exc.id == "NotImplementedError":
                    return True
            elif node.exc and isinstance(node.exc, ast.Call):
                if (
                    isinstance(node.exc.func, ast.Name)
                    and node.exc.func.id == "NotImplementedError"
                ):
                    return True
    return False


def scan_file_for_endpoints(file_path: Path) -> dict[tuple[str, str], bool]:
    """
    Scan a Python file for implemented endpoints using AST analysis.

    This replaces ~180 lines of complex regex-based parsing with clean AST traversal.

    Detection Strategy:
        1. Parse file into AST
        2. Find all urljoin() calls and extract URLs
        3. Find HTTP method calls in the same function
        4. For async files, check if function raises NotImplementedError (stub)

    Returns:
        dict: Maps (path, method) -> is_implemented
              For async files, is_implemented = False if NotImplementedError
    """
    if not file_path.exists():
        return {}

    try:
        with open(file_path) as f:
            source = f.read()
        tree = ast.parse(source)
    except SyntaxError:
        # Skip files with syntax errors
        return {}

    endpoints = {}
    is_async = "async_client" in str(file_path)

    # Walk the AST to find functions and their urljoin/HTTP method calls
    for node in ast.walk(tree):
        # Find function definitions (both regular and async)
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        # Check if this is a stub function (async only)
        is_stub = is_async and _function_raises_not_implemented(node)

        # Look for urljoin calls and HTTP method calls within this function
        urljoin_urls = []  # Store (url, line_no) tuples
        http_methods = []  # Store (method, line_no) tuples

        for child in ast.walk(node):
            if not isinstance(child, ast.Call):
                continue

            # Check if this is a urljoin() call
            func = child.func
            if isinstance(func, ast.Name) and func.id == "urljoin":
                # Extract URL from second argument
                if len(child.args) >= 2:
                    url = _extract_url_from_ast_node(child.args[1])
                    if url:
                        # Normalize URL: remove query params and trailing slash
                        url = re.sub(r"\?[^/]*$", "", url).rstrip("/")
                        if url.startswith("/rest/"):
                            urljoin_urls.append((url, child.lineno))

            # Check if this is an HTTP method call
            http_method = _get_http_method_from_call(child)
            if http_method:
                http_methods.append((http_method, child.lineno))

        # Match urljoin calls with HTTP methods in the same function
        # Heuristic: pair each urljoin with the closest HTTP method call after it
        for url, urljoin_line in urljoin_urls:
            # Find the first HTTP method call after this urljoin
            matching_methods = [
                (method, line) for method, line in http_methods if line >= urljoin_line
            ]

            if matching_methods:
                # Use the first (closest) HTTP method
                method, _ = matching_methods[0]
                is_implemented = not is_stub
                endpoints[(url, method)] = is_implemented

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
        ]
    )

    col_totals_sync = {cat: {"total": 0, "implemented": 0} for cat in method_cats}
    grand_total_sync = {"total": 0, "implemented": 0}

    sync_table_data = []
    for module in all_modules:
        row_total = {"total": 0, "implemented": 0}
        row_data = {"Module": module}

        for method_cat in method_cats:
            data = sync_stats[module][method_cat]
            if method_cat == "Write":
                row_data["Write (POST/PUT/PATCH)"] = format_cell(
                    data["implemented"], data["total"]
                )
            else:
                row_data[method_cat] = format_cell(data["implemented"], data["total"])
            row_total["total"] += data["total"]
            row_total["implemented"] += data["implemented"]
            col_totals_sync[method_cat]["total"] += data["total"]
            col_totals_sync[method_cat]["implemented"] += data["implemented"]
            grand_total_sync["total"] += data["total"]
            grand_total_sync["implemented"] += data["implemented"]

        row_data["Total"] = format_cell(row_total["implemented"], row_total["total"])
        sync_table_data.append(row_data)

    # Add totals row
    totals_row = {"Module": "**Total**"}
    for method_cat in method_cats:
        data = col_totals_sync[method_cat]
        formatted = f"**{format_cell(data['implemented'], data['total'])}**"
        if method_cat == "Write":
            totals_row["Write (POST/PUT/PATCH)"] = formatted
        else:
            totals_row[method_cat] = formatted
    totals_row["Total"] = (
        f"**{format_cell(grand_total_sync['implemented'], grand_total_sync['total'])}**"
    )
    sync_table_data.append(totals_row)

    lines.append(dict_list_to_markdown_table(sync_table_data))

    lines.append("")

    # Async table
    lines.extend(
        [
            "### Asynchronous Client",
            "",
        ]
    )

    col_totals_async = {cat: {"total": 0, "implemented": 0} for cat in method_cats}
    grand_total_async = {"total": 0, "implemented": 0}

    async_table_data = []
    for module in all_modules:
        row_total = {"total": 0, "implemented": 0}
        row_data = {"Module": module}

        for method_cat in method_cats:
            data = async_stats[module][method_cat]
            if method_cat == "Write":
                row_data["Write (POST/PUT/PATCH)"] = format_cell(
                    data["implemented"], data["total"]
                )
            else:
                row_data[method_cat] = format_cell(data["implemented"], data["total"])
            row_total["total"] += data["total"]
            row_total["implemented"] += data["implemented"]
            col_totals_async[method_cat]["total"] += data["total"]
            col_totals_async[method_cat]["implemented"] += data["implemented"]
            grand_total_async["total"] += data["total"]
            grand_total_async["implemented"] += data["implemented"]

        row_data["Total"] = format_cell(row_total["implemented"], row_total["total"])
        async_table_data.append(row_data)

    # Add totals row
    totals_row = {"Module": "**Total**"}
    for method_cat in method_cats:
        data = col_totals_async[method_cat]
        formatted = f"**{format_cell(data['implemented'], data['total'])}**"
        if method_cat == "Write":
            totals_row["Write (POST/PUT/PATCH)"] = formatted
        else:
            totals_row[method_cat] = formatted
    totals_row["Total"] = (
        f"**{format_cell(grand_total_async['implemented'], grand_total_async['total'])}**"
    )
    async_table_data.append(totals_row)

    lines.append(dict_list_to_markdown_table(async_table_data))

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
    ]

    # Add endpoint rows using pytablewriter
    endpoint_data = [
        {
            "ID": ep["id"],
            "Endpoint": f"`{ep['path']}`",
            "Module": ep["module"],
            "Method": ep["method"],
            "Status": ep["status"],
        }
        for ep in endpoints
    ]
    lines.append(dict_list_to_markdown_table(endpoint_data))

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

    # Add Endpoint ID Reference section
    lines.extend(
        [
            "",
            "## Endpoint ID Reference",
            "",
            "### ID Format: `XXYYYM`",
            "",
            "Endpoint IDs are structured 6-character codes where:",
            "",
            "- **XX** = 2-character module code",
            "- **YYY** = 3-digit zero-padded serial number (unique per endpoint path within module)",
            "- **M** = 1-character HTTP method code",
            "",
            "### Module Codes",
            "",
        ]
    )

    # Module codes table
    module_codes_data = [
        {"Code": "`CO`", "Module": "core"},
        {"Code": "`ME`", "Module": "metadata"},
        {"Code": "`CA`", "Module": "capacity"},
        {"Code": "`CB`", "Module": "collaboration"},
        {"Code": "`ST`", "Module": "statistics"},
        {"Code": "`PC`", "Module": "partscatalog"},
        {"Code": "`AU`", "Module": "auth"},
    ]
    lines.append(dict_list_to_markdown_table(module_codes_data))

    lines.extend(
        [
            "",
            "### Method Codes",
            "",
        ]
    )

    # Method codes table
    method_codes_data = [
        {"Code": "`G`", "HTTP Method": "GET"},
        {"Code": "`P`", "HTTP Method": "POST"},
        {"Code": "`U`", "HTTP Method": "PUT"},
        {"Code": "`A`", "HTTP Method": "PATCH"},
        {"Code": "`D`", "HTTP Method": "DELETE"},
    ]
    lines.append(dict_list_to_markdown_table(method_codes_data))

    lines.extend(
        [
            "",
            "### Examples",
            "",
            "- `CO001G` = Core module, first endpoint (GET method)",
            "- `ME003P` = Metadata module, third endpoint (POST method)",
            "- `CA002A` = Capacity module, second endpoint (PATCH method)",
            "- `AU001P` = Auth module, first endpoint (POST method)",
            "",
            "### Adding New Endpoints",
            "",
            "When adding new endpoints:",
            "",
            "1. **New endpoint path**: Use the next available serial number for that module",
            "2. **Existing path with new method**: Use the same serial number as the existing endpoint(s) for that path, with the appropriate method code",
            "",
            "**Example:** If `/rest/ofscCore/v1/activities` has `CO015G` (GET), adding POST would be `CO015P` (same serial number, different method letter).",
        ]
    )

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
