#!/usr/bin/env python3
"""
OFSC API Test Template Generator

This module generates comprehensive test files for OFSC API endpoints based on
the swagger specification and endpoint registry. It creates tests for:

1. All CRUD operations (if applicable)
2. Boundary test cases for each parameter
3. Negative test cases
4. Search/filter tests (for GET endpoints)
5. Pagination tests (if applicable)

Usage:
    python -m tests.utils.test_generator <endpoint_name>
    python -m tests.utils.test_generator properties
    python -m tests.utils.test_generator "activity_type_groups"
"""

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set

from tests.fixtures.endpoints_registry import (
    ENDPOINTS,
    EndpointInfo,
    EndpointParameter,
)


class CRUDPattern:
    """Represents a CRUD pattern for a resource."""

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.endpoints: Dict[str, EndpointInfo] = {}
        self.resource_name = self._extract_resource_name(base_path)
        self.has_id_parameter = "{" in base_path

    def add_endpoint(self, endpoint: EndpointInfo):
        """Add an endpoint to this CRUD pattern."""
        self.endpoints[endpoint.method] = endpoint

    def _extract_resource_name(self, path: str) -> str:
        """Extract resource name from path."""
        # Remove API prefix and version
        clean_path = re.sub(r"^/rest/ofsc\w+/v\d+/", "", path)
        # Remove path parameters
        clean_path = re.sub(r"/\{[^}]+\}.*$", "", clean_path)
        # Convert to snake_case
        resource_name = clean_path.replace("/", "_").replace("-", "_")
        return resource_name

    @property
    def has_create(self) -> bool:
        return "POST" in self.endpoints or "PUT" in self.endpoints

    @property
    def has_read(self) -> bool:
        return "GET" in self.endpoints

    @property
    def has_update(self) -> bool:
        return "PUT" in self.endpoints or "PATCH" in self.endpoints

    @property
    def has_delete(self) -> bool:
        return "DELETE" in self.endpoints

    @property
    def supports_list(self) -> bool:
        """Check if this pattern supports listing (GET without ID param)."""
        if "GET" not in self.endpoints:
            return False
        get_endpoint = self.endpoints["GET"]
        return not any(p.location == "path" for p in get_endpoint.required_parameters)


class TestTemplateGenerator:
    """Generates comprehensive test files for OFSC API endpoints."""

    def __init__(self):
        self.endpoints = ENDPOINTS
        self.crud_patterns = self._analyze_crud_patterns()

    def _analyze_crud_patterns(self) -> Dict[str, CRUDPattern]:
        """Analyze endpoints to identify CRUD patterns."""
        patterns = {}

        for endpoint in self.endpoints:
            # Group endpoints by base path (without parameters)
            base_path = re.sub(r"/\{[^}]+\}.*$", "", endpoint.path)

            if base_path not in patterns:
                patterns[base_path] = CRUDPattern(base_path)

            patterns[base_path].add_endpoint(endpoint)

        return patterns

    def find_resource_endpoints(self, resource_name: str) -> List[EndpointInfo]:
        """Find all endpoints related to a resource name."""
        resource_name = resource_name.lower().replace("_", "").replace("-", "")
        matching_endpoints = []

        for endpoint in self.endpoints:
            # Check if resource name appears in path
            path_clean = endpoint.path.lower().replace("_", "").replace("-", "")
            summary_clean = endpoint.summary.lower().replace("_", "").replace("-", "")

            if (
                resource_name in path_clean
                or resource_name in summary_clean
                or resource_name in endpoint.path.lower()
            ):
                matching_endpoints.append(endpoint)

        return matching_endpoints

    def get_crud_pattern(self, resource_name: str) -> Optional[CRUDPattern]:
        """Get CRUD pattern for a resource."""
        for pattern in self.crud_patterns.values():
            if resource_name.lower() in pattern.resource_name.lower():
                return pattern
        return None

    def generate_test_file(
        self, resource_name: str, output_path: Optional[str] = None
    ) -> str:
        """Generate a complete test file for a resource."""
        # Find matching endpoints
        endpoints = self.find_resource_endpoints(resource_name)
        if not endpoints:
            raise ValueError(f"No endpoints found for resource: {resource_name}")

        # Get CRUD pattern if available
        crud_pattern = self.get_crud_pattern(resource_name)

        # Determine output path
        if output_path is None:
            safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", resource_name.lower())
            output_path = f"tests/integration/test_{safe_name}_generated.py"

        # Generate test content
        test_content = self._generate_test_content(
            resource_name, endpoints, crud_pattern
        )

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            f.write(test_content)

        return str(output_file)

    def _generate_test_content(
        self,
        resource_name: str,
        endpoints: List[EndpointInfo],
        crud_pattern: Optional[CRUDPattern],
    ) -> str:
        """Generate the complete test file content."""

        # Organize endpoints by functionality
        get_endpoints = [ep for ep in endpoints if ep.method == "GET"]
        post_endpoints = [ep for ep in endpoints if ep.method == "POST"]
        put_endpoints = [ep for ep in endpoints if ep.method == "PUT"]
        patch_endpoints = [ep for ep in endpoints if ep.method == "PATCH"]
        delete_endpoints = [ep for ep in endpoints if ep.method == "DELETE"]

        # Determine primary module and model names
        primary_module = endpoints[0].module if endpoints else "core"
        model_names = self._extract_model_names(endpoints)

        # Generate test file sections
        sections = []

        # File header and imports
        sections.append(
            self._generate_header(resource_name, primary_module, model_names)
        )

        # Test class declaration
        sections.append(self._generate_test_class_header(resource_name))

        # Setup and fixtures
        sections.append(self._generate_setup_methods(resource_name, crud_pattern))

        # CRUD operation tests
        if crud_pattern:
            sections.extend(self._generate_crud_tests(crud_pattern))

        # Individual endpoint tests
        sections.extend(self._generate_endpoint_tests(endpoints))

        # Parameter boundary tests
        sections.extend(self._generate_parameter_tests(endpoints))

        # Negative test cases
        sections.extend(self._generate_negative_tests(endpoints))

        # Search and filter tests (for GET endpoints)
        sections.extend(self._generate_search_filter_tests(get_endpoints))

        # Pagination tests
        sections.extend(self._generate_pagination_tests(get_endpoints))

        # Performance tests
        sections.extend(self._generate_performance_tests(endpoints))

        return "\n\n".join(sections)

    def _generate_header(
        self, resource_name: str, module: str, model_names: Set[str]
    ) -> str:
        """Generate file header with imports."""
        safe_name = resource_name.replace("_", " ").title()

        # Determine imports based on module and models
        model_imports = []
        if model_names:
            model_imports = [f"    {name}," for name in sorted(model_names)]

        return f'''"""
Generated tests for {safe_name} API endpoints.

This file contains comprehensive tests for all {safe_name.lower()} operations including:
- CRUD operations
- Parameter validation
- Boundary testing
- Negative test cases
- Search and filtering
- Pagination
- Performance validation

Generated on: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}
"""

import pytest
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from ofsc.client import OFSC
from ofsc.exceptions import (
    OFSException,
    OFSValidationException,
    OFSNotFoundException, 
    OFSAuthenticationException,
    OFSRateLimitException,
)
from ofsc.models.{module} import (
{chr(10).join(model_imports) if model_imports else "    # Model imports will be added based on endpoint analysis"}
)
from tests.utils.base_test import BaseOFSCTest
from tests.utils.factories import (
    create_test_translation,
    create_test_user,
    create_test_resource,
    create_test_activity,
    create_test_property,
    create_test_workskill,
    create_test_capacity_area,
)'''

    def _generate_test_class_header(self, resource_name: str) -> str:
        """Generate test class header."""
        class_name = "".join(
            word.capitalize() for word in resource_name.replace("-", "_").split("_")
        )

        return f'''class Test{class_name}API(BaseOFSCTest):
    """Comprehensive tests for {resource_name.replace("_", " ").title()} API endpoints."""
    
    @pytest.fixture(autouse=True)
    async def setup_client(self, async_client):
        """Setup OFSC client for tests."""
        self.client = async_client
        
        # Set default rate limiting for API tests
        self.set_rate_limit_delay(0.1)'''

    def _generate_setup_methods(
        self, resource_name: str, crud_pattern: Optional[CRUDPattern]
    ) -> str:
        """Generate setup methods and fixtures."""
        setup_methods = []

        # Generate shared test data setup if CRUD operations are available
        if crud_pattern and crud_pattern.has_create:
            setup_methods.append(f'''    
    @pytest.fixture(autouse=True)
    async def setup_test_data(self):
        """Setup shared test data for {resource_name} tests."""
        # Generate unique identifiers for test resources
        self.test_{resource_name}_label = self.generate_unique_label('{resource_name}')
        self.test_{resource_name}_name = f"Test {resource_name.replace("_", " ").title()} {{self.test_{resource_name}_label}}"
        
        # Create test data that will be used across multiple tests
        self.test_{resource_name}_data = {{
            'label': self.test_{resource_name}_label,
            'name': self.test_{resource_name}_name,
            # Add additional test data fields based on resource schema
        }}
        
        # Initialize list to track created resources for cleanup
        self.created_{resource_name}_ids = []''')

        # Generate helper methods
        setup_methods.append(f'''    
    def _create_test_{resource_name}_data(self, **overrides) -> Dict[str, Any]:
        """Create test data for {resource_name} with optional overrides."""
        data = {{
            'label': self.generate_unique_label('{resource_name}'),
            'name': f"Test {resource_name.replace("_", " ").title()} {{datetime.now().strftime('%H%M%S')}}",
            # Add resource-specific default fields here
        }}
        data.update(overrides)
        return data
    
    def _validate_{resource_name}_response(self, response_data: Dict[str, Any]) -> None:
        """Validate {resource_name} response structure."""
        # Add resource-specific validation logic
        assert 'label' in response_data, "Response missing 'label' field"
        assert 'name' in response_data, "Response missing 'name' field"
        # Add additional validation based on schema''')

        return "\n".join(setup_methods)

    def _generate_crud_tests(self, crud_pattern: CRUDPattern) -> List[str]:
        """Generate CRUD operation tests."""
        tests = []

        if crud_pattern.has_create:
            tests.append(self._generate_create_test(crud_pattern))

        if crud_pattern.has_read:
            tests.append(self._generate_read_test(crud_pattern))

            if crud_pattern.supports_list:
                tests.append(self._generate_list_test(crud_pattern))

        if crud_pattern.has_update:
            tests.append(self._generate_update_test(crud_pattern))

        if crud_pattern.has_delete:
            tests.append(self._generate_delete_test(crud_pattern))

        return tests

    def _generate_create_test(self, crud_pattern: CRUDPattern) -> str:
        """Generate create operation test."""
        create_endpoint = crud_pattern.endpoints.get(
            "POST"
        ) or crud_pattern.endpoints.get("PUT")
        if not create_endpoint:
            return f"# No create endpoint found for {crud_pattern.resource_name}"
        resource_name = crud_pattern.resource_name

        return f'''    async def test_create_{resource_name}(self):
        """Test creating a new {resource_name.replace("_", " ")}."""
        # Set endpoint context for error reporting
        self.set_endpoint_context(endpoint_id={create_endpoint.id})
        
        # Create test data
        {resource_name}_data = self._create_test_{resource_name}_data()
        
        # Define cleanup function
        async def cleanup_{resource_name}():
            try:
                if hasattr(self.client.{crud_pattern.endpoints[list(crud_pattern.endpoints.keys())[0]].module}, 'delete_{resource_name}'):
                    await self.client.{crud_pattern.endpoints[list(crud_pattern.endpoints.keys())[0]].module}.delete_{resource_name}({resource_name}_data['label'])
            except OFSNotFoundException:
                pass  # Already deleted
        
        # Create {resource_name} with performance tracking
        async with self.track_performance('create_{resource_name}'):
            async with self.api_call_context(endpoint_id={create_endpoint.id}):
                created_{resource_name} = await self.client.{create_endpoint.module}.create_{resource_name}(
                    {resource_name}_data['label'], {resource_name}_data
                )
        
        # Track for cleanup
        self.track_resource('{resource_name}', {resource_name}_data['label'], cleanup_{resource_name})
        
        # Validate response
        self.assert_pydantic_model_valid(created_{resource_name}.dict(), type(created_{resource_name}))
        self._validate_{resource_name}_response(created_{resource_name}.dict())
        
        # Verify created data matches input
        assert created_{resource_name}.label == {resource_name}_data['label']
        assert created_{resource_name}.name == {resource_name}_data['name']
        
        # Assert creation performance
        self.assert_response_time_acceptable('create_{resource_name}', max_seconds=3.0)'''

    def _generate_read_test(self, crud_pattern: CRUDPattern) -> str:
        """Generate read operation test."""
        get_endpoint = crud_pattern.endpoints["GET"]
        resource_name = crud_pattern.resource_name

        return f'''    async def test_get_{resource_name}_by_id(self):
        """Test retrieving a specific {resource_name.replace("_", " ")} by ID."""
        # Set endpoint context
        self.set_endpoint_context(endpoint_id={get_endpoint.id})
        
        # First create a test {resource_name} to retrieve
        {resource_name}_data = self._create_test_{resource_name}_data()
        
        # Create the resource (assuming create method exists)
        if hasattr(self.client.{get_endpoint.module}, 'create_{resource_name}'):
            created_{resource_name} = await self.create_test_resource(
                '{resource_name}',
                lambda: self.client.{get_endpoint.module}.create_{resource_name}(
                    {resource_name}_data['label'], {resource_name}_data
                ),
                lambda: self.client.{get_endpoint.module}.delete_{resource_name}({resource_name}_data['label'])
            )
        else:
            pytest.skip("Create method not available for {resource_name}")
        
        # Retrieve the {resource_name}
        async with self.track_performance('get_{resource_name}'):
            async with self.api_call_context(endpoint_id={get_endpoint.id}):
                retrieved_{resource_name} = await self.client.{get_endpoint.module}.get_{resource_name}(
                    {resource_name}_data['label']
                )
        
        # Validate response
        self.assert_pydantic_model_valid(retrieved_{resource_name}.dict(), type(retrieved_{resource_name}))
        self._validate_{resource_name}_response(retrieved_{resource_name}.dict())
        
        # Verify retrieved data matches created data
        assert retrieved_{resource_name}.label == created_{resource_name}.label
        assert retrieved_{resource_name}.name == created_{resource_name}.name
        
        # Assert retrieval performance
        self.assert_response_time_acceptable('get_{resource_name}', max_seconds=2.0)'''

    def _generate_list_test(self, crud_pattern: CRUDPattern) -> str:
        """Generate list operation test."""
        get_endpoint = crud_pattern.endpoints["GET"]
        resource_name = crud_pattern.resource_name

        return f'''    async def test_list_{resource_name}s(self):
        """Test listing {resource_name.replace("_", " ")}s."""
        # Set endpoint context
        self.set_endpoint_context(endpoint_id={get_endpoint.id})
        
        # Get list of {resource_name}s
        async with self.track_performance('list_{resource_name}s'):
            async with self.api_call_context(endpoint_id={get_endpoint.id}):
                {resource_name}s_response = await self.client.{get_endpoint.module}.get_{resource_name}s(limit=10)
        
        # Validate response structure
        response_data = {resource_name}s_response.dict()
        self.assert_response_structure(response_data)
        
        # Validate that we got a list
        assert 'items' in response_data, "Response should contain 'items' field"
        items = response_data['items']
        
        # Validate each item in the list
        for item in items:
            self._validate_{resource_name}_response(item)
        
        # Validate pagination fields
        assert 'offset' in response_data
        assert 'limit' in response_data
        assert 'hasMore' in response_data
        
        # Assert list performance
        self.assert_response_time_acceptable('list_{resource_name}s', max_seconds=5.0)'''

    def _generate_update_test(self, crud_pattern: CRUDPattern) -> str:
        """Generate update operation test."""
        update_endpoint = crud_pattern.endpoints.get(
            "PUT"
        ) or crud_pattern.endpoints.get("PATCH")
        if not update_endpoint:
            return f"# No update endpoint found for {crud_pattern.resource_name}"
        resource_name = crud_pattern.resource_name

        return f'''    async def test_update_{resource_name}(self):
        """Test updating an existing {resource_name.replace("_", " ")}."""
        # Set endpoint context
        self.set_endpoint_context(endpoint_id={update_endpoint.id})
        
        # Create test {resource_name} first
        {resource_name}_data = self._create_test_{resource_name}_data()
        
        created_{resource_name} = await self.create_test_resource(
            '{resource_name}',
            lambda: self.client.{update_endpoint.module}.create_{resource_name}(
                {resource_name}_data['label'], {resource_name}_data
            ),
            lambda: self.client.{update_endpoint.module}.delete_{resource_name}({resource_name}_data['label'])
        )
        
        # Prepare updated data
        updated_data = {resource_name}_data.copy()
        updated_data['name'] = f"Updated {{updated_data['name']}}"
        
        # Update the {resource_name}
        async with self.track_performance('update_{resource_name}'):
            async with self.api_call_context(endpoint_id={update_endpoint.id}):
                updated_{resource_name} = await self.client.{update_endpoint.module}.update_{resource_name}(
                    {resource_name}_data['label'], updated_data
                )
        
        # Validate response
        self.assert_pydantic_model_valid(updated_{resource_name}.dict(), type(updated_{resource_name}))
        self._validate_{resource_name}_response(updated_{resource_name}.dict())
        
        # Verify updates were applied
        assert updated_{resource_name}.name == updated_data['name']
        assert updated_{resource_name}.label == {resource_name}_data['label']  # Should remain same
        
        # Assert update performance
        self.assert_response_time_acceptable('update_{resource_name}', max_seconds=3.0)'''

    def _generate_delete_test(self, crud_pattern: CRUDPattern) -> str:
        """Generate delete operation test."""
        delete_endpoint = crud_pattern.endpoints.get("DELETE")
        if not delete_endpoint:
            return f"# No delete endpoint found for {crud_pattern.resource_name}"
        resource_name = crud_pattern.resource_name

        return f'''    async def test_delete_{resource_name}(self):
        """Test deleting a {resource_name.replace("_", " ")}."""
        # Set endpoint context
        self.set_endpoint_context(endpoint_id={delete_endpoint.id})
        
        # Create test {resource_name} first
        {resource_name}_data = self._create_test_{resource_name}_data()
        
        # Create without automatic cleanup (we're testing deletion)
        created_{resource_name} = await self.client.{delete_endpoint.module}.create_{resource_name}(
            {resource_name}_data['label'], {resource_name}_data
        )
        
        # Delete the {resource_name}
        async with self.track_performance('delete_{resource_name}'):
            async with self.api_call_context(endpoint_id={delete_endpoint.id}):
                await self.client.{delete_endpoint.module}.delete_{resource_name}(
                    {resource_name}_data['label']
                )
        
        # Verify deletion by attempting to retrieve (should fail)
        async with self.expect_exception(OFSNotFoundException):
            await self.client.{delete_endpoint.module}.get_{resource_name}({resource_name}_data['label'])
        
        # Assert deletion performance
        self.assert_response_time_acceptable('delete_{resource_name}', max_seconds=3.0)'''

    def _generate_endpoint_tests(self, endpoints: List[EndpointInfo]) -> List[str]:
        """Generate individual endpoint tests."""
        tests = []

        for endpoint in endpoints:
            test_name = self._generate_test_method_name(endpoint)
            tests.append(f'''    async def {test_name}(self):
        """Test {endpoint.summary.lower()}."""
        # Set endpoint context
        self.set_endpoint_context(endpoint_id={endpoint.id})
        
        # TODO: Implement specific test logic for {endpoint.method} {endpoint.path}
        # This test was auto-generated and needs implementation details
        
        async with self.track_performance('{test_name}'):
            async with self.api_call_context(endpoint_id={endpoint.id}):
                # Add actual API call here
                pass
        
        # Add response validation
        # Add performance assertions''')

        return tests

    def _generate_parameter_tests(self, endpoints: List[EndpointInfo]) -> List[str]:
        """Generate parameter boundary tests."""
        tests = []

        for endpoint in endpoints:
            # Generate tests for each parameter
            for param in endpoint.required_parameters + endpoint.optional_parameters:
                tests.extend(self._generate_parameter_boundary_tests(endpoint, param))

        return tests

    def _generate_parameter_boundary_tests(
        self, endpoint: EndpointInfo, param: EndpointParameter
    ) -> List[str]:
        """Generate boundary tests for a specific parameter."""
        tests = []
        param_name = param.name.replace("-", "_")
        test_base_name = f"test_{endpoint.method.lower()}_{param_name}_boundary"

        # Length boundary tests
        if param.min_length is not None or param.max_length is not None:
            tests.append(f'''    async def {test_base_name}_length(self):
        """Test {param.name} parameter length boundaries."""
        self.set_endpoint_context(endpoint_id={endpoint.id})
        
        # Test minimum length boundary
        {
                f"min_length_value = 'a' * {param.min_length}"
                if param.min_length
                else "# No minimum length constraint"
            }
        {
                f"max_length_value = 'a' * {param.max_length}"
                if param.max_length
                else "# No maximum length constraint"
            }
        
        # Test just over maximum length (should fail)
        {
                f"""
        if {param.max_length}:
            async with self.expect_exception(OFSValidationException):
                over_max_value = 'a' * ({param.max_length} + 1)
                # TODO: Add actual API call with over_max_value
        """
                if param.max_length
                else ""
            }
        
        # Test just under minimum length (should fail) 
        {
                f"""
        if {param.min_length} > 0:
            async with self.expect_exception(OFSValidationException):
                under_min_value = 'a' * ({param.min_length} - 1)
                # TODO: Add actual API call with under_min_value
        """
                if param.min_length
                else ""
            }''')

        # Numeric boundary tests
        if param.minimum is not None or param.maximum is not None:
            tests.append(f'''    async def {test_base_name}_numeric(self):
        """Test {param.name} parameter numeric boundaries."""
        self.set_endpoint_context(endpoint_id={endpoint.id})
        
        # Test boundary values
        {
                f"min_value = {param.minimum}"
                if param.minimum is not None
                else "# No minimum value constraint"
            }
        {
                f"max_value = {param.maximum}"
                if param.maximum is not None
                else "# No maximum value constraint"
            }
        
        # Test values outside boundaries (should fail)
        {
                f"""
        async with self.expect_exception(OFSValidationException):
            # TODO: Add API call with value below minimum: {param.minimum - 1}
            pass
        """
                if param.minimum is not None
                else ""
            }
        
        {
                f"""
        async with self.expect_exception(OFSValidationException):
            # TODO: Add API call with value above maximum: {param.maximum + 1}
            pass
        """
                if param.maximum is not None
                else ""
            }''')

        # Enum value tests
        if param.enum:
            tests.append(f'''    async def {test_base_name}_enum(self):
        """Test {param.name} parameter enum values."""
        self.set_endpoint_context(endpoint_id={endpoint.id})
        
        # Valid enum values: {param.enum}
        for valid_value in {param.enum}:
            # TODO: Add API call with valid_value
            pass
        
        # Test invalid enum value (should fail)
        async with self.expect_exception(OFSValidationException):
            # TODO: Add API call with invalid enum value
            pass''')

        return tests

    def _generate_negative_tests(self, endpoints: List[EndpointInfo]) -> List[str]:
        """Generate negative test cases."""
        tests = []

        for endpoint in endpoints:
            tests.append(self._generate_not_found_test(endpoint))
            tests.append(self._generate_invalid_parameter_test(endpoint))

            if (
                endpoint.method in ["POST", "PUT", "PATCH"]
                and endpoint.request_body_schema
            ):
                tests.append(self._generate_invalid_request_body_test(endpoint))

        return tests

    def _generate_not_found_test(self, endpoint: EndpointInfo) -> str:
        """Generate not found test."""
        method_name = self._generate_test_method_name(endpoint, suffix="not_found")

        return f'''    async def {method_name}(self):
        """Test {endpoint.method} {endpoint.path} with non-existent resource."""
        self.set_endpoint_context(endpoint_id={endpoint.id})
        
        # Test with non-existent resource ID
        async with self.expect_exception(OFSNotFoundException):
            # TODO: Add API call with non-existent resource ID
            # Example: nonexistent_id = "nonexistent_resource_12345"
            pass'''

    def _generate_invalid_parameter_test(self, endpoint: EndpointInfo) -> str:
        """Generate invalid parameter test."""
        method_name = self._generate_test_method_name(endpoint, suffix="invalid_params")

        return f'''    async def {method_name}(self):
        """Test {endpoint.method} {endpoint.path} with invalid parameters."""
        self.set_endpoint_context(endpoint_id={endpoint.id})
        
        # Test with invalid parameter types/values
        async with self.expect_exception(OFSValidationException):
            # TODO: Add API call with invalid parameters
            # Examples:
            # - Invalid type: string where integer expected
            # - Out of range values
            # - Invalid format
            pass'''

    def _generate_invalid_request_body_test(self, endpoint: EndpointInfo) -> str:
        """Generate invalid request body test."""
        method_name = self._generate_test_method_name(endpoint, suffix="invalid_body")

        return f'''    async def {method_name}(self):
        """Test {endpoint.method} {endpoint.path} with invalid request body."""
        self.set_endpoint_context(endpoint_id={endpoint.id})
        
        # Test with invalid request body
        async with self.expect_exception(OFSValidationException):
            # TODO: Add API call with invalid request body
            # Examples:
            # - Missing required fields
            # - Invalid field types
            # - Invalid field values
            pass'''

    def _generate_search_filter_tests(
        self, get_endpoints: List[EndpointInfo]
    ) -> List[str]:
        """Generate search and filter tests for GET endpoints."""
        tests = []

        for endpoint in get_endpoints:
            # Check if endpoint supports search/filter parameters
            search_params = [
                p
                for p in endpoint.optional_parameters
                if any(
                    keyword in p.name.lower()
                    for keyword in ["search", "filter", "query", "q"]
                )
            ]

            if search_params:
                tests.append(self._generate_search_test(endpoint, search_params))

            # Check for other filter parameters
            filter_params = [
                p
                for p in endpoint.optional_parameters
                if p.name.lower() not in ["offset", "limit", "fields"]
            ]

            if filter_params:
                tests.append(self._generate_filter_test(endpoint, filter_params))

        return tests

    def _generate_search_test(
        self, endpoint: EndpointInfo, search_params: List[EndpointParameter]
    ) -> str:
        """Generate search functionality test."""
        method_name = self._generate_test_method_name(endpoint, suffix="search")

        return f'''    async def {method_name}(self):
        """Test search functionality for {endpoint.path}."""
        self.set_endpoint_context(endpoint_id={endpoint.id})
        
        # Test search with various query terms
        search_terms = ["test", "sample", "*", ""]
        
        for term in search_terms:
            async with self.track_performance(f'search_{{term or "empty"}}'):
                async with self.api_call_context(endpoint_id={endpoint.id}):
                    # TODO: Add actual search API call
                    # Example: await self.client.{endpoint.module}.search_method(q=term)
                    pass
            
            # Validate search results
            # TODO: Add search result validation
        
        # Assert search performance
        self.assert_response_time_acceptable('search_test', max_seconds=5.0)'''

    def _generate_filter_test(
        self, endpoint: EndpointInfo, filter_params: List[EndpointParameter]
    ) -> str:
        """Generate filter functionality test."""
        method_name = self._generate_test_method_name(endpoint, suffix="filter")

        return f'''    async def {method_name}(self):
        """Test filter functionality for {endpoint.path}."""
        self.set_endpoint_context(endpoint_id={endpoint.id})
        
        # Test various filter combinations
        filter_combinations = [
            # TODO: Add realistic filter combinations based on available parameters
            # Parameters available: {[p.name for p in filter_params]}
        ]
        
        for filters in filter_combinations:
            async with self.track_performance('filter_test'):
                async with self.api_call_context(endpoint_id={endpoint.id}):
                    # TODO: Add actual filter API call
                    pass
            
            # Validate filtered results
            # TODO: Add filter result validation
        
        # Assert filter performance
        self.assert_response_time_acceptable('filter_test', max_seconds=5.0)'''

    def _generate_pagination_tests(
        self, get_endpoints: List[EndpointInfo]
    ) -> List[str]:
        """Generate pagination tests for GET endpoints."""
        tests = []

        for endpoint in get_endpoints:
            # Check if endpoint supports pagination
            has_offset = any(
                p.name.lower() == "offset" for p in endpoint.optional_parameters
            )
            has_limit = any(
                p.name.lower() == "limit" for p in endpoint.optional_parameters
            )

            if has_offset and has_limit:
                tests.append(self._generate_pagination_test(endpoint))

        return tests

    def _generate_pagination_test(self, endpoint: EndpointInfo) -> str:
        """Generate pagination test."""
        method_name = self._generate_test_method_name(endpoint, suffix="pagination")

        return f'''    async def {method_name}(self):
        """Test pagination for {endpoint.path}."""
        self.set_endpoint_context(endpoint_id={endpoint.id})
        
        # Test different page sizes
        page_sizes = [1, 5, 10, 50, 100]
        
        for limit in page_sizes:
            async with self.track_performance(f'pagination_limit_{{limit}}'):
                async with self.api_call_context(endpoint_id={endpoint.id}):
                    # TODO: Add actual paginated API call
                    # Example: response = await self.client.{endpoint.module}.get_method(limit=limit, offset=0)
                    pass
            
            # Validate pagination response
            # TODO: Add pagination validation
            # - Check items count <= limit
            # - Check hasMore field
            # - Check totalResults/totalCount
        
        # Test pagination traversal
        all_items = []
        offset = 0
        limit = 10
        
        while True:
            async with self.api_call_context(endpoint_id={endpoint.id}):
                # TODO: Add actual paginated API call
                # response = await self.client.{endpoint.module}.get_method(limit=limit, offset=offset)
                break  # Remove this when implementing
            
            # TODO: Add items to all_items and check hasMore
            # if not response.hasMore:
            #     break
            # offset += limit
        
        # Validate complete pagination
        # TODO: Validate that all items were retrieved
        
        # Assert pagination performance
        self.assert_response_time_acceptable('pagination_limit_10', max_seconds=3.0)'''

    def _generate_performance_tests(self, endpoints: List[EndpointInfo]) -> List[str]:
        """Generate performance tests."""
        tests = []

        # Generate bulk operation performance test
        get_endpoints = [ep for ep in endpoints if ep.method == "GET"]
        if get_endpoints:
            tests.append(self._generate_bulk_performance_test(get_endpoints[0]))

        # Generate concurrent access test
        if endpoints:
            tests.append(self._generate_concurrent_test(endpoints[0]))

        return tests

    def _generate_bulk_performance_test(self, endpoint: EndpointInfo) -> str:
        """Generate bulk performance test."""
        method_name = self._generate_test_method_name(
            endpoint, suffix="bulk_performance"
        )

        return f'''    async def {method_name}(self):
        """Test bulk operations performance for {endpoint.path}."""
        self.set_endpoint_context(endpoint_id={endpoint.id})
        
        # Perform multiple operations in sequence
        operation_count = 10
        
        async with self.track_performance('bulk_operations'):
            for i in range(operation_count):
                async with self.api_call_context(endpoint_id={endpoint.id}):
                    # TODO: Add actual API call
                    pass
        
        # Analyze performance metrics
        metrics = self.get_performance_summary()
        bulk_metrics = metrics.get('bulk_operations', {{}})
        
        # Assert reasonable performance
        if bulk_metrics:
            avg_time = bulk_metrics['average']
            total_time = bulk_metrics['total']
            
            assert avg_time < 2.0, f"Average operation time too slow: {{avg_time:.3f}}s"
            assert total_time < 30.0, f"Total bulk operation time too slow: {{total_time:.3f}}s"'''

    def _generate_concurrent_test(self, endpoint: EndpointInfo) -> str:
        """Generate concurrent access test."""
        method_name = self._generate_test_method_name(endpoint, suffix="concurrent")

        return f'''    async def {method_name}(self):
        """Test concurrent access to {endpoint.path}."""
        import asyncio
        
        self.set_endpoint_context(endpoint_id={endpoint.id})
        
        # Define concurrent operation
        async def concurrent_operation(operation_id: int):
            async with self.api_call_context(endpoint_id={endpoint.id}):
                # TODO: Add actual API call
                # Consider using different parameters per operation to avoid conflicts
                pass
        
        # Run multiple operations concurrently
        concurrent_count = 5
        
        async with self.track_performance('concurrent_operations'):
            tasks = [concurrent_operation(i) for i in range(concurrent_count)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Validate that all operations completed successfully
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                pytest.fail(f"Concurrent operation {{i}} failed: {{result}}")
        
        # Assert concurrent performance
        self.assert_response_time_acceptable('concurrent_operations', max_seconds=10.0)'''

    def _generate_test_method_name(
        self, endpoint: EndpointInfo, suffix: str = None
    ) -> str:
        """Generate a test method name for an endpoint."""
        # Clean up the path to create a method name
        path_parts = endpoint.path.split("/")
        relevant_parts = [
            part
            for part in path_parts
            if part
            and not part.startswith("{")
            and "rest" not in part
            and "ofsc" not in part
            and "v1" not in part
            and "v2" not in part
        ]

        method_name = f"test_{endpoint.method.lower()}_{'_'.join(relevant_parts)}"

        if suffix:
            method_name += f"_{suffix}"

        # Clean up the method name
        method_name = re.sub(r"[^a-zA-Z0-9_]", "_", method_name)
        method_name = re.sub(r"_+", "_", method_name)

        return method_name

    def _extract_model_names(self, endpoints: List[EndpointInfo]) -> Set[str]:
        """Extract model names from endpoints."""
        models = set()

        for endpoint in endpoints:
            if endpoint.response_schema:
                models.add(endpoint.response_schema)
            if endpoint.request_body_schema:
                models.add(endpoint.request_body_schema)

        return models


def main():
    """Main function for command line usage."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive test files for OFSC API endpoints"
    )
    parser.add_argument(
        "resource_name",
        help='Name of the resource to generate tests for (e.g., "properties", "activities")',
    )
    parser.add_argument(
        "--output", "-o", help="Output file path (default: auto-generated)"
    )
    parser.add_argument(
        "--list-resources", "-l", action="store_true", help="List available resources"
    )

    args = parser.parse_args()

    generator = TestTemplateGenerator()

    if args.list_resources:
        print("Available resources based on endpoint analysis:")
        resources = set()
        for pattern in generator.crud_patterns.values():
            resources.add(pattern.resource_name)

        for resource in sorted(resources):
            print(f"  - {resource}")
        return

    try:
        output_file = generator.generate_test_file(args.resource_name, args.output)
        print(f"Generated test file: {output_file}")

        # Show summary
        endpoints = generator.find_resource_endpoints(args.resource_name)
        print(f"Found {len(endpoints)} endpoints for '{args.resource_name}':")
        for ep in endpoints:
            print(f"  - {ep.method} {ep.path}")

    except ValueError as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
