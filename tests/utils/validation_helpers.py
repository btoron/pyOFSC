"""Validation helper functions for tests."""

from typing import Any, Dict, Type, Optional
from pydantic import BaseModel


def remove_metadata_from_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove _metadata field from response data.
    
    Args:
        response_data: Response data dictionary
        
    Returns:
        Response data without _metadata field
    """
    data = response_data.copy()
    if "_metadata" in data:
        del data["_metadata"]
    return data


def validate_model_from_response(
    model_class: Type[BaseModel], 
    response_data: Dict[str, Any], 
    items_key: str = "items"
) -> bool:
    """Validate a model class against response data.
    
    Args:
        model_class: Pydantic model class to validate
        response_data: Response data containing items
        items_key: Key containing the list of items (default: "items")
        
    Returns:
        True if all items validate successfully
        
    Raises:
        ValidationError: If any item fails validation
    """
    clean_data = remove_metadata_from_response(response_data)
    
    if items_key in clean_data:
        for item in clean_data[items_key]:
            model_class(**item)
    else:
        # Single item response
        model_class(**clean_data)
    
    return True


def validate_list_response(
    model_class: Type[BaseModel],
    response_data: Dict[str, Any],
    items_key: str = "items",
    min_items: Optional[int] = None
) -> list[BaseModel]:
    """Validate and return list of models from response.
    
    Args:
        model_class: Pydantic model class to validate
        response_data: Response data containing items
        items_key: Key containing the list of items (default: "items")
        min_items: Minimum number of items expected (optional)
        
    Returns:
        List of validated model instances
        
    Raises:
        ValidationError: If any item fails validation
        AssertionError: If min_items check fails
    """
    clean_data = remove_metadata_from_response(response_data)
    items = clean_data.get(items_key, [])
    
    if min_items is not None:
        assert len(items) >= min_items, f"Expected at least {min_items} items, got {len(items)}"
    
    return [model_class(**item) for item in items]


def assert_base_response_fields(response_data: Dict[str, Any]) -> None:
    """Assert that response contains expected base fields.
    
    Args:
        response_data: Response data to check
        
    Raises:
        AssertionError: If required fields are missing
    """
    # Check for pagination fields in list responses
    if "items" in response_data:
        assert "offset" in response_data, "List response missing 'offset' field"
        assert "limit" in response_data, "List response missing 'limit' field"
        assert "hasMore" in response_data, "List response missing 'hasMore' field"
        assert "totalResults" in response_data or "totalCount" in response_data, \
            "List response missing total count field"
    
    # Check for links if present
    if "links" in response_data:
        assert isinstance(response_data["links"], list), "Links should be a list"
        for link in response_data["links"]:
            assert "rel" in link, "Link missing 'rel' field"
            assert "href" in link, "Link missing 'href' field"


def validate_error_response(
    response_data: Dict[str, Any],
    expected_status: Optional[str] = None,
    expected_code: Optional[str] = None
) -> None:
    """Validate an error response structure.
    
    Args:
        response_data: Error response data
        expected_status: Expected error status (optional)
        expected_code: Expected error code (optional)
        
    Raises:
        AssertionError: If validation fails
    """
    assert "status" in response_data, "Error response missing 'status' field"
    assert "title" in response_data, "Error response missing 'title' field"
    
    if expected_status:
        assert response_data["status"] == expected_status, \
            f"Expected status '{expected_status}', got '{response_data['status']}'"
    
    if expected_code and "code" in response_data:
        assert response_data["code"] == expected_code, \
            f"Expected code '{expected_code}', got '{response_data['code']}'"