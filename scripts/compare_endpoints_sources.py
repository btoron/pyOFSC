#!/usr/bin/env python3
"""
Compare ENDPOINTS.md documentation with endpoints_registry.py to identify discrepancies.

This script compares:
1. Implementation status between the two sources
2. Method signatures between the two sources
3. Missing endpoints in either source
4. Inconsistent data

Usage:
    python scripts/compare_endpoints_sources.py
"""

import re
import sys
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass

# Add the project root to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.fixtures.endpoints_registry import ENDPOINTS, EndpointInfo


@dataclass
class EndpointDoc:
    """Represents an endpoint from ENDPOINTS.md"""

    id: int
    path: str
    method: str
    module: str
    implemented_in: str
    signature: str


def parse_endpoints_md(file_path: str) -> Dict[int, EndpointDoc]:
    """Parse ENDPOINTS.md and extract endpoint information."""
    endpoints = {}

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

            # Clean up signature - remove markdown backticks
            if signature.startswith("`") and signature.endswith("`"):
                signature = signature[1:-1]

            endpoints[endpoint_id] = EndpointDoc(
                id=endpoint_id,
                path=path,
                method=method,
                module=module,
                implemented_in=implemented_in,
                signature=signature,
            )

    return endpoints


def normalize_signature(signature: str) -> str:
    """Normalize signature for comparison by removing extra whitespace."""
    if not signature:
        return ""

    # Remove extra whitespace and normalize spacing
    normalized = re.sub(r"\s+", " ", signature.strip())
    return normalized


def compare_implementation_status(
    registry_endpoint: EndpointInfo, doc_endpoint: EndpointDoc
) -> List[str]:
    """Compare implementation status between registry and documentation."""
    issues = []

    # Check if implementation status matches
    registry_implemented = bool(registry_endpoint.implemented_in)
    # For doc, check if it has a version number (not empty, not "DEPRECATED", and not just a version like "v3.0.0-dev")
    doc_has_version = bool(
        doc_endpoint.implemented_in
        and doc_endpoint.implemented_in != ""
        and doc_endpoint.implemented_in.upper() != "DEPRECATED"
    )

    # Only compare implementation status, not the actual values since they represent different things
    # Registry has method references, doc has version numbers
    if registry_implemented and not doc_has_version:
        issues.append(
            f"✅ Registry shows implemented ({registry_endpoint.implemented_in}) but doc shows not implemented"
        )
    elif not registry_implemented and doc_has_version:
        issues.append(
            f"❌ Doc shows implemented (version: {doc_endpoint.implemented_in}) but registry shows not implemented"
        )

    # Don't compare the actual values since registry has method refs and doc has versions

    return issues


def compare_signatures(
    registry_endpoint: EndpointInfo, doc_endpoint: EndpointDoc
) -> List[str]:
    """Compare method signatures between registry and documentation."""
    issues = []

    registry_sig = normalize_signature(registry_endpoint.signature)
    doc_sig = normalize_signature(doc_endpoint.signature)

    # Only compare if both have signatures
    if registry_sig and doc_sig:
        if registry_sig != doc_sig:
            issues.append("📝 Signature mismatch:")
            issues.append(f"   Registry: {registry_sig}")
            issues.append(f"   Doc:      {doc_sig}")
    elif registry_sig and not doc_sig:
        issues.append(f"📝 Registry has signature but doc missing: {registry_sig}")
    elif not registry_sig and doc_sig:
        issues.append(f"📝 Doc has signature but registry missing: {doc_sig}")

    return issues


def compare_basic_info(
    registry_endpoint: EndpointInfo, doc_endpoint: EndpointDoc
) -> List[str]:
    """Compare basic endpoint information."""
    issues = []

    if registry_endpoint.path != doc_endpoint.path:
        issues.append(
            f"🛤️ Path mismatch: Registry='{registry_endpoint.path}' vs Doc='{doc_endpoint.path}'"
        )

    if registry_endpoint.method != doc_endpoint.method:
        issues.append(
            f"📋 Method mismatch: Registry='{registry_endpoint.method}' vs Doc='{doc_endpoint.method}'"
        )

    if registry_endpoint.module != doc_endpoint.module:
        issues.append(
            f"📦 Module mismatch: Registry='{registry_endpoint.module}' vs Doc='{doc_endpoint.module}'"
        )

    return issues


def generate_comparison_report():
    """Generate comprehensive comparison report."""

    print("=" * 80)
    print("🔍 ENDPOINTS COMPARISON REPORT")
    print("=" * 80)
    print("Comparing ENDPOINTS.md with endpoints_registry.py")
    print()

    # Load documentation endpoints
    endpoints_md_path = "docs/ENDPOINTS.md"
    if not Path(endpoints_md_path).exists():
        print(f"❌ Error: {endpoints_md_path} not found")
        return

    doc_endpoints = parse_endpoints_md(endpoints_md_path)
    print(f"📋 Loaded {len(doc_endpoints)} endpoints from ENDPOINTS.md")

    # Create registry lookup by ID
    registry_by_id = {ep.id: ep for ep in ENDPOINTS}
    print(f"📋 Loaded {len(registry_by_id)} endpoints from registry")
    print()

    # Track statistics
    total_issues = 0
    endpoints_with_issues = 0
    implementation_issues = 0
    signature_issues = 0
    missing_in_registry = 0
    missing_in_doc = 0

    # Compare endpoints present in both sources
    for endpoint_id in sorted(set(doc_endpoints.keys()) | set(registry_by_id.keys())):
        doc_endpoint = doc_endpoints.get(endpoint_id)
        registry_endpoint = registry_by_id.get(endpoint_id)

        endpoint_issues = []

        if not doc_endpoint:
            endpoint_issues.append("📋 Missing in ENDPOINTS.md")
            missing_in_doc += 1
        elif not registry_endpoint:
            endpoint_issues.append("🗂️ Missing in endpoints_registry.py")
            missing_in_registry += 1
        else:
            # Compare basic info
            basic_issues = compare_basic_info(registry_endpoint, doc_endpoint)
            endpoint_issues.extend(basic_issues)

            # Compare implementation status
            impl_issues = compare_implementation_status(registry_endpoint, doc_endpoint)
            endpoint_issues.extend(impl_issues)
            if impl_issues:
                implementation_issues += 1

            # Compare signatures
            sig_issues = compare_signatures(registry_endpoint, doc_endpoint)
            endpoint_issues.extend(sig_issues)
            if sig_issues:
                signature_issues += 1

        # Report issues for this endpoint
        if endpoint_issues:
            endpoints_with_issues += 1
            total_issues += len(endpoint_issues)

            # Get endpoint details for header
            path = doc_endpoint.path if doc_endpoint else registry_endpoint.path
            method = doc_endpoint.method if doc_endpoint else registry_endpoint.method
            module = doc_endpoint.module if doc_endpoint else registry_endpoint.module

            print(f"🚨 ID {endpoint_id}: {method} {path} ({module})")
            for issue in endpoint_issues:
                print(f"   {issue}")
            print()

    # Summary report
    print("=" * 80)
    print("📊 SUMMARY REPORT")
    print("=" * 80)
    print(f"Total endpoints compared: {max(len(doc_endpoints), len(registry_by_id))}")
    print(f"Endpoints with issues: {endpoints_with_issues}")
    print(f"Total issues found: {total_issues}")
    print()
    print("Issue breakdown:")
    print(f"  📋 Missing in ENDPOINTS.md: {missing_in_doc}")
    print(f"  🗂️ Missing in registry: {missing_in_registry}")
    print(f"  💻 Implementation discrepancies: {implementation_issues}")
    print(f"  📝 Signature discrepancies: {signature_issues}")
    print()

    if total_issues == 0:
        print("✅ No discrepancies found! Both sources are in sync.")
    else:
        print(f"⚠️ Found {total_issues} discrepancies that need attention.")
        print()
        print("Recommendations:")
        if missing_in_doc > 0:
            print(f"  1. Add {missing_in_doc} missing endpoints to ENDPOINTS.md")
        if missing_in_registry > 0:
            print(
                f"  2. Investigate {missing_in_registry} endpoints missing from registry"
            )
        if implementation_issues > 0:
            print(
                f"  3. Sync implementation status for {implementation_issues} endpoints"
            )
        if signature_issues > 0:
            print(f"  4. Update signatures for {signature_issues} endpoints")


if __name__ == "__main__":
    generate_comparison_report()
