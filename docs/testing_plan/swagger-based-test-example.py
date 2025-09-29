# tests/fixtures/parameters/activities_from_swagger.py
"""
Example of how to generate test parameters from actual Swagger/OpenAPI specification.
This would be generated after parsing your swagger.json file.
"""

from typing import Dict, Any, List
from tests.utils.parameter_testing import ParameterTestCase, TestCategory

# This would be loaded from your actual swagger.json
SWAGGER_ACTIVITY_SCHEMA = {
    "paths": {
        "/rest/ofscCore/v2/activities": {
            "post": {
                "summary": "Create activity",
                "operationId": "createActivity",
                "parameters": [],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/CreateActivityRequest"
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Activity created successfully",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ActivityResponse"
                                }
                            }
                        },
                    }
                },
            }
        },
        "/rest/ofscCore/v2/activities/{activityId}": {
            "get": {
                "summary": "Get activity by ID",
                "operationId": "getActivity",
                "parameters": [
                    {
                        "name": "activityId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
            },
            "patch": {"summary": "Update activity", "operationId": "updateActivity"},
            "delete": {"summary": "Delete activity", "operationId": "deleteActivity"},
        },
    },
    "components": {
        "schemas": {
            "CreateActivityRequest": {
                "type": "object",
                "required": ["activityType", "name", "duration"],
                "properties": {
                    "activityType": {
                        "type": "string",
                        "enum": ["service", "install", "repair", "delivery"],
                        "description": "Type of activity",
                    },
                    "name": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 255,
                        "description": "Activity name",
                    },
                    "duration": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 1440,
                        "description": "Duration in minutes",
                    },
                    "date": {
                        "type": "string",
                        "format": "date",
                        "description": "Scheduled date (YYYY-MM-DD)",
                    },
                    "timeSlot": {
                        "type": "string",
                        "enum": ["all-day", "AM", "PM", "2hr", "4hr"],
                        "default": "all-day",
                    },
                    "customer": {"$ref": "#/components/schemas/CustomerInfo"},
                    "address": {"$ref": "#/components/schemas/Address"},
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "maxItems": 10,
                    },
                    "inventoryList": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/InventoryItem"},
                    },
                    "workZone": {"type": "string", "maxLength": 50},
                    "priority": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 10,
                        "default": 5,
                    },
                },
            },
            "CustomerInfo": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "maxLength": 100},
                    "phone": {"type": "string", "pattern": "^\\+?[1-9]\\d{1,14}$"},
                    "email": {"type": "string", "format": "email"},
                },
            },
        }
    },
}


def generate_test_cases_from_swagger(schema: Dict[str, Any]) -> List[ParameterTestCase]:
    """Generate test cases based on Swagger schema definition"""
    test_cases = []

    # Extract schema details
    create_schema = schema["components"]["schemas"]["CreateActivityRequest"]
    required_fields = create_schema.get("required", [])
    properties = create_schema.get("properties", {})

    # Generate test cases for each field based on its schema
    for field_name, field_schema in properties.items():
        field_type = field_schema.get("type")

        if field_type == "string":
            # String field tests
            if "enum" in field_schema:
                # Test each enum value
                for enum_value in field_schema["enum"]:
                    test_cases.append(
                        ParameterTestCase(
                            test_id=f"{field_name}_enum_{enum_value}",
                            description=f"Test {field_name} with enum value: {enum_value}",
                            category=TestCategory.HAPPY_PATH,
                            parameters=create_minimal_params(
                                {field_name: enum_value}, required_fields, properties
                            ),
                            tags=[field_name, "enum"],
                        )
                    )

                # Test invalid enum
                test_cases.append(
                    ParameterTestCase(
                        test_id=f"{field_name}_invalid_enum",
                        description=f"Test {field_name} with invalid enum value",
                        category=TestCategory.NEGATIVE,
                        parameters=create_minimal_params(
                            {field_name: "INVALID"}, required_fields, properties
                        ),
                        expected_status=400,
                        expected_error=f"Invalid {field_name}",
                        should_cleanup=False,
                        tags=[field_name, "enum", "negative"],
                    )
                )

            # String length tests
            if "minLength" in field_schema or "maxLength" in field_schema:
                min_len = field_schema.get("minLength", 0)
                max_len = field_schema.get("maxLength", 1000)

                # Boundary tests
                test_cases.extend(
                    [
                        ParameterTestCase(
                            test_id=f"{field_name}_min_length",
                            description=f"Test {field_name} at minimum length ({min_len})",
                            category=TestCategory.BOUNDARY,
                            parameters=create_minimal_params(
                                {field_name: "A" * min_len}, required_fields, properties
                            ),
                            tags=[field_name, "boundary", "minLength"],
                        ),
                        ParameterTestCase(
                            test_id=f"{field_name}_max_length",
                            description=f"Test {field_name} at maximum length ({max_len})",
                            category=TestCategory.BOUNDARY,
                            parameters=create_minimal_params(
                                {field_name: "A" * max_len}, required_fields, properties
                            ),
                            tags=[field_name, "boundary", "maxLength"],
                        ),
                        ParameterTestCase(
                            test_id=f"{field_name}_over_max_length",
                            description=f"Test {field_name} over maximum length",
                            category=TestCategory.NEGATIVE,
                            parameters=create_minimal_params(
                                {field_name: "A" * (max_len + 1)},
                                required_fields,
                                properties,
                            ),
                            expected_status=400,
                            expected_error=f"{field_name} too long",
                            should_cleanup=False,
                            tags=[field_name, "boundary", "negative"],
                        ),
                    ]
                )

        elif field_type == "integer":
            # Integer field tests
            min_val = field_schema.get("minimum", 0)
            max_val = field_schema.get("maximum", 2147483647)

            test_cases.extend(
                [
                    ParameterTestCase(
                        test_id=f"{field_name}_minimum",
                        description=f"Test {field_name} at minimum value ({min_val})",
                        category=TestCategory.BOUNDARY,
                        parameters=create_minimal_params(
                            {field_name: min_val}, required_fields, properties
                        ),
                        tags=[field_name, "boundary", "minimum"],
                    ),
                    ParameterTestCase(
                        test_id=f"{field_name}_maximum",
                        description=f"Test {field_name} at maximum value ({max_val})",
                        category=TestCategory.BOUNDARY,
                        parameters=create_minimal_params(
                            {field_name: max_val}, required_fields, properties
                        ),
                        tags=[field_name, "boundary", "maximum"],
                    ),
                    ParameterTestCase(
                        test_id=f"{field_name}_below_minimum",
                        description=f"Test {field_name} below minimum value",
                        category=TestCategory.NEGATIVE,
                        parameters=create_minimal_params(
                            {field_name: min_val - 1}, required_fields, properties
                        ),
                        expected_status=400,
                        expected_error=f"{field_name} too small",
                        should_cleanup=False,
                        tags=[field_name, "boundary", "negative"],
                    ),
                ]
            )

        elif field_type == "array":
            # Array field tests
            max_items = field_schema.get("maxItems", 100)

            test_cases.extend(
                [
                    ParameterTestCase(
                        test_id=f"{field_name}_empty_array",
                        description=f"Test {field_name} with empty array",
                        category=TestCategory.BOUNDARY,
                        parameters=create_minimal_params(
                            {field_name: []}, required_fields, properties
                        ),
                        tags=[field_name, "array", "empty"],
                    ),
                    ParameterTestCase(
                        test_id=f"{field_name}_max_items",
                        description=f"Test {field_name} with maximum items ({max_items})",
                        category=TestCategory.BOUNDARY,
                        parameters=create_minimal_params(
                            {field_name: [f"item_{i}" for i in range(max_items)]},
                            required_fields,
                            properties,
                        ),
                        tags=[field_name, "array", "maxItems"],
                    ),
                ]
            )

    # Test missing required fields
    for required_field in required_fields:
        params = create_minimal_params({}, required_fields, properties)
        params.pop(required_field, None)

        test_cases.append(
            ParameterTestCase(
                test_id=f"missing_required_{required_field}",
                description=f"Test with missing required field: {required_field}",
                category=TestCategory.NEGATIVE,
                parameters=params,
                expected_status=400,
                expected_error=f"{required_field} is required",
                should_cleanup=False,
                tags=["required", "negative", required_field],
            )
        )

    return test_cases


def create_minimal_params(
    overrides: Dict[str, Any], required_fields: List[str], properties: Dict[str, Any]
) -> Dict[str, Any]:
    """Create minimal valid parameters with overrides"""
    params = {}

    # Add required fields with default values
    for field in required_fields:
        if field not in overrides:
            field_schema = properties.get(field, {})
            params[field] = get_default_value(field, field_schema)

    # Apply overrides
    params.update(overrides)

    return params


def get_default_value(field_name: str, field_schema: Dict[str, Any]) -> Any:
    """Get a default valid value for a field based on its schema"""
    field_type = field_schema.get("type")

    if "default" in field_schema:
        return field_schema["default"]

    if field_type == "string":
        if "enum" in field_schema:
            return field_schema["enum"][0]
        elif field_name == "name":
            return "Test Activity"
        elif field_name == "date":
            from datetime import datetime

            return datetime.now().strftime("%Y-%m-%d")
        else:
            return "test_value"

    elif field_type == "integer":
        if field_name == "duration":
            return 60
        elif field_name == "priority":
            return 5
        else:
            return field_schema.get("minimum", 1)

    elif field_type == "array":
        return []

    elif field_type == "object":
        return {}

    return None


# Generate test cases from swagger
ACTIVITY_TEST_CASES = generate_test_cases_from_swagger(SWAGGER_ACTIVITY_SCHEMA)

# Add custom test cases for complex scenarios
ACTIVITY_TEST_CASES.extend(
    [
        ParameterTestCase(
            test_id="complex_activity_full",
            description="Create activity with all optional fields populated",
            category=TestCategory.HAPPY_PATH,
            parameters={
                "activityType": "install",
                "name": "Complete Installation Package",
                "duration": 240,
                "date": "2024-12-01",
                "timeSlot": "AM",
                "customer": {
                    "name": "John Doe",
                    "phone": "+1234567890",
                    "email": "john.doe@example.com",
                },
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "postalCode": "12345",
                },
                "skills": ["electrical", "plumbing", "hvac"],
                "workZone": "ZONE_A",
                "priority": 8,
            },
            tags=["complex", "full"],
        ),
        ParameterTestCase(
            test_id="special_characters_all_fields",
            description="Test special characters in all string fields",
            category=TestCategory.EDGE_CASE,
            parameters={
                "activityType": "service",
                "name": 'Test & Co. "Special" <Activity>',
                "duration": 60,
                "customer": {
                    "name": "O'Brien & Associates",
                    "email": "test+special@example.com",
                },
                "workZone": "Zone-A/B",
            },
            tags=["special_chars", "edge_case"],
        ),
    ]
)


# Example of how to use these in a test
def get_test_cases_for_endpoint(
    endpoint: str, operation: str
) -> List[ParameterTestCase]:
    """Get test cases for a specific endpoint and operation"""
    if endpoint == "activities" and operation == "create":
        return ACTIVITY_TEST_CASES
    # Add other endpoints as needed
    return []
