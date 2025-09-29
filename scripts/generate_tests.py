#!/usr/bin/env python3
"""
OFSC Test Generator CLI

Command-line interface for generating comprehensive test files for OFSC API endpoints.

Usage:
    python scripts/generate_tests.py <resource_name>
    python scripts/generate_tests.py properties
    python scripts/generate_tests.py --list
    python scripts/generate_tests.py activities --output tests/custom/my_activity_tests.py
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.utils.test_generator import TestTemplateGenerator


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive test files for OFSC API endpoints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate tests for properties endpoints
  python scripts/generate_tests.py properties
  
  # Generate tests for activities with custom output path
  python scripts/generate_tests.py activities --output tests/custom/activity_tests.py
  
  # List all available resources
  python scripts/generate_tests.py --list
  
  # Generate tests for a specific resource pattern
  python scripts/generate_tests.py workSkills
        """,
    )

    parser.add_argument(
        "resource_name",
        nargs="?",
        help='Name of the resource to generate tests for (e.g., "properties", "activities", "users")',
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: tests/integration/test_<resource>_generated.py)",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="List all available resources that can be tested",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Show what would be generated without creating files",
    )

    args = parser.parse_args()

    generator = TestTemplateGenerator()

    if args.list:
        print("📋 Available resources for test generation:")
        print("=" * 50)

        # Group resources by module
        resources_by_module = {}
        for pattern in generator.crud_patterns.values():
            if pattern.resource_name.startswith("_rest_"):
                continue  # Skip internal endpoints

            # Try to determine module from endpoints
            if pattern.endpoints:
                module = list(pattern.endpoints.values())[0].module
                if module not in resources_by_module:
                    resources_by_module[module] = []
                resources_by_module[module].append(pattern.resource_name)

        for module, resources in sorted(resources_by_module.items()):
            print(f"\n🔧 {module.upper()} Module:")
            for resource in sorted(resources):
                # Get endpoint count for this resource
                endpoints = generator.find_resource_endpoints(resource)
                crud_pattern = generator.get_crud_pattern(resource)

                operations = []
                if crud_pattern:
                    if crud_pattern.has_create:
                        operations.append("CREATE")
                    if crud_pattern.has_read:
                        operations.append("READ")
                    if crud_pattern.has_update:
                        operations.append("UPDATE")
                    if crud_pattern.has_delete:
                        operations.append("DELETE")

                ops_str = "/".join(operations) if operations else "N/A"
                print(f"  • {resource:<30} ({len(endpoints)} endpoints, {ops_str})")

        print(f"\n💡 Usage: python {sys.argv[0]} <resource_name>")
        return 0

    if not args.resource_name:
        parser.error("resource_name is required when not using --list")

    try:
        if args.dry_run:
            print(f"🔍 Analyzing resource: '{args.resource_name}'")
            endpoints = generator.find_resource_endpoints(args.resource_name)

            if not endpoints:
                print(f"❌ No endpoints found for resource: {args.resource_name}")
                print("💡 Use --list to see available resources")
                return 1

            print(f"✅ Found {len(endpoints)} endpoints:")
            for ep in endpoints:
                print(f"  • {ep.method} {ep.path} - {ep.summary}")

            crud_pattern = generator.get_crud_pattern(args.resource_name)
            if crud_pattern:
                operations = []
                if crud_pattern.has_create:
                    operations.append("CREATE")
                if crud_pattern.has_read:
                    operations.append("READ")
                if crud_pattern.has_update:
                    operations.append("UPDATE")
                if crud_pattern.has_delete:
                    operations.append("DELETE")

                print(
                    f"🔄 CRUD Operations: {'/'.join(operations) if operations else 'None detected'}"
                )

            output_path = (
                args.output
                or f"tests/integration/test_{args.resource_name.lower().replace(' ', '_').replace('-', '_')}_generated.py"
            )
            print(f"📁 Would generate: {output_path}")
            return 0

        if args.verbose:
            print(f"🚀 Generating tests for resource: '{args.resource_name}'")

        output_file = generator.generate_test_file(args.resource_name, args.output)

        print(f"✅ Successfully generated test file: {output_file}")

        # Show summary
        endpoints = generator.find_resource_endpoints(args.resource_name)
        print(f"📊 Generated tests for {len(endpoints)} endpoints:")

        if args.verbose:
            for ep in endpoints:
                print(f"  • {ep.method} {ep.path} - {ep.summary}")
        else:
            # Group by method
            methods = {}
            for ep in endpoints:
                if ep.method not in methods:
                    methods[ep.method] = 0
                methods[ep.method] += 1

            method_summary = ", ".join(
                f"{count} {method}" for method, count in sorted(methods.items())
            )
            print(f"  📈 Methods: {method_summary}")

        # Show what types of tests were generated
        crud_pattern = generator.get_crud_pattern(args.resource_name)
        if crud_pattern:
            test_types = []
            if crud_pattern.has_create:
                test_types.append("✨ Create")
            if crud_pattern.has_read:
                test_types.append("👁️ Read")
                if crud_pattern.supports_list:
                    test_types.append("📋 List")
            if crud_pattern.has_update:
                test_types.append("✏️ Update")
            if crud_pattern.has_delete:
                test_types.append("🗑️ Delete")

            if test_types:
                print(f"🔄 CRUD Tests: {', '.join(test_types)}")

        print(
            "🧪 Additional Tests: Parameter boundaries, Negative cases, Pagination, Performance"
        )
        print(f"📖 Next: Review and customize the generated tests in {output_file}")

    except ValueError as e:
        print(f"❌ Error: {e}")
        print("💡 Use --list to see available resources")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
