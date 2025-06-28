"""Mockup requests module for OFSC Python Wrapper.

This module provides a complete mockup of the requests library interface
to resolve dependency issues and enable testing without requiring the
actual requests package. It implements all the functionality currently
used in the OFSC codebase.

This is a temporary solution until Phase 1.6 migration to httpx is completed.
"""

import json
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlencode


class MockResponse:
    """Mock response object that mimics requests.Response interface."""
    
    def __init__(
        self,
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text_data: str = "",
        content_data: bytes = b"",
        headers: Optional[Dict[str, str]] = None,
        elapsed_ms: int = 100
    ):
        """Initialize mock response.
        
        Args:
            status_code: HTTP status code (default: 200)
            json_data: JSON response data (default: empty dict)
            text_data: Text response data
            content_data: Binary response data  
            headers: Response headers
            elapsed_ms: Request duration in milliseconds
        """
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text_data or json.dumps(self._json_data)
        self.content = content_data or self.text.encode('utf-8')
        self.headers = headers or {'content-type': 'application/json'}
        self.elapsed = timedelta(milliseconds=elapsed_ms)
        
    def json(self) -> Dict[str, Any]:
        """Return JSON response data."""
        if self._json_data:
            return self._json_data
        try:
            return json.loads(self.text)
        except json.JSONDecodeError:
            return {}


# Global configuration for mock responses
_mock_config = {
    'default_status': 200,
    'default_response': {},
    'enable_logging': False,
    'response_mappings': {}
}


def configure_mock(
    default_status: int = 200,
    default_response: Optional[Dict[str, Any]] = None,
    enable_logging: bool = False,
    response_mappings: Optional[Dict[str, Dict[str, Any]]] = None
):
    """Configure global mock behavior.
    
    Args:
        default_status: Default HTTP status code
        default_response: Default JSON response data
        enable_logging: Whether to log requests (for debugging)
        response_mappings: URL pattern to response mappings
    """
    global _mock_config
    _mock_config.update({
        'default_status': default_status,
        'default_response': default_response or {},
        'enable_logging': enable_logging,
        'response_mappings': response_mappings or {}
    })


def _log_request(method: str, url: str, **kwargs) -> None:
    """Log request details if logging is enabled."""
    if _mock_config['enable_logging']:
        print(f"MOCK REQUEST: {method.upper()} {url}")
        if kwargs.get('headers'):
            print(f"  Headers: {kwargs['headers']}")
        if kwargs.get('params'):
            print(f"  Params: {kwargs['params']}")
        if kwargs.get('data'):
            print(f"  Data: {kwargs['data']}")
        if kwargs.get('json'):
            print(f"  JSON: {kwargs['json']}")


def _create_response(method: str, url: str, **kwargs) -> MockResponse:
    """Create a mock response based on configuration and request details."""
    _log_request(method, url, **kwargs)
    
    # Check for specific URL mappings
    for pattern, response_config in _mock_config['response_mappings'].items():
        if pattern in url:
            return MockResponse(
                status_code=response_config.get('status_code', 200),
                json_data=response_config.get('json', {}),
                text_data=response_config.get('text', ''),
                headers=response_config.get('headers', {}),
                elapsed_ms=response_config.get('elapsed_ms', 100)
            )
    
    # Default successful response
    if method.upper() == 'DELETE':
        # DELETE requests typically return 204 No Content
        return MockResponse(
            status_code=204,
            json_data={},
            text_data='',
            elapsed_ms=50
        )
    elif method.upper() == 'POST':
        # POST requests typically return 201 Created
        return MockResponse(
            status_code=201,
            json_data=_mock_config['default_response'],
            elapsed_ms=150
        )
    else:
        # GET, PUT, PATCH return 200 OK
        return MockResponse(
            status_code=_mock_config['default_status'],
            json_data=_mock_config['default_response'],
            elapsed_ms=100
        )


def get(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> MockResponse:
    """Mock HTTP GET request.
    
    Args:
        url: Request URL
        params: Query parameters
        headers: Request headers
        **kwargs: Additional request parameters
        
    Returns:
        MockResponse object
    """
    # Build full URL with query parameters
    if params:
        query_string = urlencode(params)
        url = f"{url}?{query_string}"
    
    return _create_response('GET', url, params=params, headers=headers, **kwargs)


def post(
    url: str,
    data: Optional[Union[str, bytes]] = None,
    json: Optional[Dict[str, Any]] = None,
    files: Optional[List[Tuple[str, Any]]] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> MockResponse:
    """Mock HTTP POST request.
    
    Args:
        url: Request URL
        data: Request body data
        json: JSON request body
        files: File upload data
        headers: Request headers
        **kwargs: Additional request parameters
        
    Returns:
        MockResponse object
    """
    return _create_response(
        'POST', url, 
        data=data, json=json, files=files, headers=headers, 
        **kwargs
    )


def put(
    url: str,
    data: Optional[Union[str, bytes]] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> MockResponse:
    """Mock HTTP PUT request.
    
    Args:
        url: Request URL
        data: Request body data
        json: JSON request body
        headers: Request headers
        **kwargs: Additional request parameters
        
    Returns:
        MockResponse object
    """
    return _create_response(
        'PUT', url,
        data=data, json=json, headers=headers,
        **kwargs
    )


def patch(
    url: str,
    data: Optional[Union[str, bytes]] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> MockResponse:
    """Mock HTTP PATCH request.
    
    Args:
        url: Request URL
        data: Request body data
        json: JSON request body
        headers: Request headers
        **kwargs: Additional request parameters
        
    Returns:
        MockResponse object
    """
    return _create_response(
        'PATCH', url,
        data=data, json=json, headers=headers,
        **kwargs
    )


def delete(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> MockResponse:
    """Mock HTTP DELETE request.
    
    Args:
        url: Request URL
        headers: Request headers
        **kwargs: Additional request parameters
        
    Returns:
        MockResponse object
    """
    return _create_response('DELETE', url, headers=headers, **kwargs)


# Type alias for compatibility with type hints
Response = MockResponse


# Exception classes for compatibility (not used in current codebase but good to have)
class RequestException(Exception):
    """Base exception for request errors."""
    pass


class HTTPError(RequestException):
    """HTTP error exception."""
    pass


class ConnectionError(RequestException):
    """Connection error exception."""
    pass


class Timeout(RequestException):
    """Request timeout exception."""
    pass


# Convenience functions for testing
def set_mock_response(
    url_pattern: str,
    status_code: int = 200,
    json_data: Optional[Dict[str, Any]] = None,
    text_data: str = "",
    headers: Optional[Dict[str, str]] = None,
    elapsed_ms: int = 100
):
    """Set a specific mock response for URLs matching a pattern.
    
    Args:
        url_pattern: URL pattern to match
        status_code: HTTP status code to return
        json_data: JSON response data
        text_data: Text response data
        headers: Response headers
        elapsed_ms: Request duration in milliseconds
    """
    global _mock_config
    _mock_config['response_mappings'][url_pattern] = {
        'status_code': status_code,
        'json': json_data or {},
        'text': text_data,
        'headers': headers or {},
        'elapsed_ms': elapsed_ms
    }


def clear_mock_responses():
    """Clear all configured mock responses."""
    global _mock_config
    _mock_config['response_mappings'] = {}


def enable_request_logging(enabled: bool = True):
    """Enable or disable request logging for debugging.
    
    Args:
        enabled: Whether to enable logging
    """
    global _mock_config
    _mock_config['enable_logging'] = enabled


# Example usage for setting up realistic responses:
def setup_ofsc_mock_responses():
    """Set up realistic mock responses for OFSC API endpoints."""
    
    # Metadata endpoints
    set_mock_response(
        '/rest/ofscMetadata/',
        status_code=200,
        json_data={
            'items': [],
            'totalResults': 0,
            'hasMore': False,
            'limit': 100,
            'offset': 0
        }
    )
    
    # Core endpoints
    set_mock_response(
        '/rest/ofscCore/',
        status_code=200,
        json_data={'success': True}
    )
    
    # Capacity endpoints
    set_mock_response(
        '/rest/ofscCapacity/',
        status_code=200,
        json_data={'success': True}
    )
    
    # OAuth token endpoint
    set_mock_response(
        '/rest/ofscOAuth/',
        status_code=200,
        json_data={
            'access_token': 'mock_token_12345',
            'token_type': 'Bearer',
            'expires_in': 3600
        }
    )


# Auto-setup realistic responses on import
setup_ofsc_mock_responses()