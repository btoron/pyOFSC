"""Response handling utilities for OFSC Python Wrapper v3.0.

This module provides utilities for parsing httpx responses into Pydantic models
while preserving the raw response data. It supports both sync and async patterns
and handles error responses appropriately.
"""

from typing import Type, TypeVar, Any, Dict
import json

try:
    import httpx
except ImportError:
    httpx = None

from pydantic import BaseModel, ValidationError

from ..models.base import OFSResponseList
from ..exceptions import create_exception_from_response, OFSValidationException

T = TypeVar("T", bound=BaseModel)


class ResponseHandler:
    """Handles parsing of httpx responses into Pydantic models."""

    @staticmethod
    def parse_response(
        response: "httpx.Response", model_class: Type[T], auto_model: bool = True
    ) -> T:
        """
        Parse httpx response into a Pydantic model instance.

        Args:
            response: The httpx response object
            model_class: The Pydantic model class to parse into
            auto_model: Whether to automatically detect model type from response

        Returns:
            Instance of the model class with raw response attached

        Raises:
            OFSAPIError: If response indicates an API error
            ValidationError: If response data doesn't match model schema
        """
        # Check for HTTP errors first - always raise exceptions (R7.3)
        if response.status_code >= 400:
            raise create_exception_from_response(response)

        try:
            # Parse JSON response
            data = response.json()
        except json.JSONDecodeError as e:
            raise OFSValidationException(
                f"Invalid JSON response: {e}",
                response=response,
                request_details={
                    "url": str(response.url),
                    "method": response.request.method if response.request else None,
                },
            )

        # Remove metadata if present (API metadata, not model data)
        if isinstance(data, dict) and "_metadata" in data:
            data = {k: v for k, v in data.items() if k != "_metadata"}

        try:
            # Use BaseOFSResponse.from_response if available
            if hasattr(model_class, "from_response"):
                return model_class.from_response(response, **{})
            else:
                # Fallback to regular validation with manual response attachment
                instance = model_class.model_validate(data)
                if hasattr(instance, "_raw_response"):
                    instance._raw_response = response
                return instance

        except ValidationError as e:
            raise OFSValidationException(
                f"Response validation failed for {model_class.__name__}: {e}",
                validation_errors=e.errors() if hasattr(e, "errors") else [],
                response=response,
                request_details={
                    "url": str(response.url),
                    "method": response.request.method if response.request else None,
                },
            )

    @staticmethod
    def parse_list_response(
        response: "httpx.Response", item_model_class: Type[T], auto_model: bool = True
    ) -> "OFSResponseList[T]":
        """
        Parse httpx response into a paginated list response.

        Args:
            response: The httpx response object
            item_model_class: The Pydantic model class for list items
            auto_model: Whether to automatically detect model type from response

        Returns:
            OFSResponseList instance with items and pagination info

        Raises:
            OFSAPIError: If response indicates an API error
            ValidationError: If response data doesn't match expected schema
        """
        # Check for HTTP errors first - always raise exceptions (R7.3)
        if response.status_code >= 400:
            raise create_exception_from_response(response)

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise OFSValidationException(
                f"Invalid JSON response: {e}",
                response=response,
                request_details={
                    "url": str(response.url),
                    "method": response.request.method if response.request else None,
                },
            )

        # Remove metadata if present
        if isinstance(data, dict) and "_metadata" in data:
            data = {k: v for k, v in data.items() if k != "_metadata"}

        try:
            # Create generic OFSResponseList with the item type
            list_class = OFSResponseList[item_model_class]
            return list_class.from_response(response)

        except ValidationError as e:
            raise OFSValidationException(
                f"List response validation failed for {item_model_class.__name__}: {e}",
                validation_errors=e.errors() if hasattr(e, "errors") else [],
                response=response,
                request_details={
                    "url": str(response.url),
                    "method": response.request.method if response.request else None,
                },
            )

    # Note: _handle_error_response removed - now using create_exception_from_response directly

    @staticmethod
    def is_paginated_response(data: Dict[str, Any]) -> bool:
        """
        Check if response data represents a paginated list.

        Args:
            data: The parsed JSON response data

        Returns:
            True if data appears to be a paginated response
        """
        if not isinstance(data, dict):
            return False

        # Check for standard pagination fields
        pagination_fields = {"items", "totalResults", "hasMore", "limit", "offset"}
        return bool(pagination_fields.intersection(data.keys()))

    @staticmethod
    def extract_items_from_response(data: Dict[str, Any]) -> list:
        """
        Extract items list from response data.

        Args:
            data: The parsed JSON response data

        Returns:
            List of items, or empty list if no items found
        """
        if isinstance(data, dict) and "items" in data:
            return data["items"] or []
        elif isinstance(data, list):
            return data
        else:
            return []


# Convenience functions for backward compatibility
def parse_response(
    response: "httpx.Response", model_class: Type[T], auto_model: bool = True
) -> T:
    """Parse httpx response into a Pydantic model instance."""
    return ResponseHandler.parse_response(response, model_class, auto_model)


def parse_list_response(
    response: "httpx.Response", item_model_class: Type[T], auto_model: bool = True
) -> "OFSResponseList[T]":
    """Parse httpx response into a paginated list response."""
    return ResponseHandler.parse_list_response(response, item_model_class, auto_model)
