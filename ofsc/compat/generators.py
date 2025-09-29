"""Dynamic method generation for backward compatibility wrapper.

This module provides utilities to dynamically generate synchronous wrapper methods
that internally call the async v3.0 API methods.
"""

import inspect
from typing import Any, Callable, Dict

from ..client import OFSC as AsyncOFSC


def create_sync_method(
    api_name: str, method_name: str, method_config: Dict[str, Any]
) -> Callable:
    """Create a synchronous wrapper method for an async API method.

    Args:
        api_name: Name of the API (e.g., 'core', 'metadata', 'capacity')
        method_name: Name of the method (e.g., 'get_users')
        method_config: Method configuration including params and defaults

    Returns:
        A synchronous method that wraps the async call
    """
    params = method_config.get("params", [])
    defaults = method_config.get("defaults", {})
    doc = method_config.get("doc", f"{method_name} method")

    def sync_method(self, *args, **kwargs):
        """Synchronous wrapper for async API method."""
        # Apply parameter defaults
        final_kwargs = defaults.copy()

        # Map positional args to parameter names
        for i, arg in enumerate(args):
            if i < len(params):
                final_kwargs[params[i]] = arg

        # Override with explicit kwargs
        final_kwargs.update(kwargs)

        # Remove self reference and config from kwargs if present
        final_kwargs.pop("self", None)

        async def _async_call():
            async with AsyncOFSC(**self._config) as client:
                api = getattr(client, api_name)
                if api is None:
                    raise NotImplementedError(
                        f"{api_name} API not yet implemented in v3.0"
                    )

                method = getattr(api, method_name)
                if method is None:
                    raise AttributeError(
                        f"Method {method_name} not found in {api_name} API"
                    )

                return await method(**final_kwargs)

        return self._run_async(_async_call())

    # Set method metadata
    sync_method.__name__ = method_name
    sync_method.__doc__ = f"""{doc}.
    
    This is a backward compatibility wrapper over the async v3.0 API.
    Returns the same Pydantic models as the async API.
    
    Parameters:
        {", ".join(f"{param}" for param in params)}
    """

    # Create proper signature
    sig_params = []
    for param in params:
        if param in defaults:
            # Parameter has default value
            sig_params.append(
                inspect.Parameter(
                    param,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=defaults[param],
                )
            )
        else:
            # Required parameter
            sig_params.append(
                inspect.Parameter(param, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            )

    sync_method.__signature__ = inspect.Signature(sig_params)

    return sync_method


def create_deprecated_method(
    original_name: str, new_api: str, new_method: str
) -> Callable:
    """Create a deprecated method that redirects to the new API structure.

    Args:
        original_name: Original method name (e.g., 'get_users')
        new_api: New API name (e.g., 'core')
        new_method: New method name (e.g., 'get_users')

    Returns:
        A method that warns about deprecation and redirects to new API
    """

    def deprecated_method(self, *args, **kwargs):
        import warnings

        warnings.warn(
            f"{original_name} is deprecated. Use client.{new_api}.{new_method}() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Redirect to new API method
        return getattr(self, new_method)(*args, **kwargs)

    deprecated_method.__name__ = original_name
    deprecated_method.__doc__ = (
        f"""DEPRECATED: Use client.{new_api}.{new_method}() instead."""
    )

    return deprecated_method


def apply_method_mappings(cls, method_mappings: Dict[str, Dict[str, Any]]):
    """Apply method mappings to a class by creating wrapper methods.

    Args:
        cls: The class to add methods to
        method_mappings: Dictionary of API mappings
    """
    for api_name, methods in method_mappings.items():
        for method_name, method_config in methods.items():
            # Create the sync wrapper method
            sync_method = create_sync_method(api_name, method_name, method_config)

            # Add method to class
            setattr(cls, method_name, sync_method)


def create_property_methods(cls, api_name: str):
    """Create property methods for API access (e.g., client.core, client.metadata).

    Args:
        cls: The class to add properties to
        api_name: Name of the API
    """

    def api_property(self):
        """API property that returns a namespace object with methods."""
        if not hasattr(self, f"_{api_name}_api"):
            # Create a namespace object that has all the API methods
            namespace = type(f"{api_name.title()}API", (), {})()

            # Get method mappings for this API
            from .method_mappings import get_all_methods

            all_methods = get_all_methods()

            if api_name in all_methods:
                for method_name, method_config in all_methods[api_name].items():
                    sync_method = create_sync_method(
                        api_name, method_name, method_config
                    )

                    # Bind self to the method
                    def create_bound_method(sm):
                        return lambda *args, **kwargs: sm(self, *args, **kwargs)

                    bound_method = create_bound_method(sync_method)
                    bound_method.__name__ = sync_method.__name__
                    bound_method.__doc__ = sync_method.__doc__
                    setattr(namespace, method_name, bound_method)

            setattr(self, f"_{api_name}_api", namespace)

        return getattr(self, f"_{api_name}_api")

    # Add as property to class
    setattr(cls, api_name, property(api_property))
