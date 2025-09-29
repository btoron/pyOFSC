"""Backward compatibility wrapper for OFSC v3.0.

This module provides a synchronous wrapper that maintains the v2.x API while internally
using the new async-only v3.0 architecture.
"""

import asyncio
import atexit
import logging
import warnings
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from .method_mappings import get_all_methods


class OFSC:
    """Backward compatibility wrapper providing sync API over async v3.0 architecture.

    This class provides the same API as OFSC v2.x while internally using the new
    async-only v3.0 client. All methods return the same Pydantic models as the
    async API for consistency.

    Usage:
        from ofsc.compat import OFSC

        # Same API as v2.x
        client = OFSC(instance="demo", client_id="id", client_secret="secret")
        users = client.get_users()  # Returns UserListResponse

        # Context manager support
        with OFSC(instance="demo", client_id="id", client_secret="secret") as client:
            users = client.get_users()

    Note:
        This wrapper creates an event loop for each instance and runs async methods
        synchronously. For better performance, consider migrating to the async API:

        from ofsc import OFSC
        async with OFSC(...) as client:
            users = await client.core.get_users()
    """

    def __init__(
        self,
        instance: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        **kwargs,
    ):
        """Initialize the backward compatibility wrapper.

        Args:
            instance: OFSC instance name
            client_id: Client ID for authentication
            client_secret: Client secret for authentication
            **kwargs: Additional arguments passed to the async client
        """
        # Issue light deprecation warning
        warnings.warn(
            "Sync OFSC is deprecated. Consider migrating to async for better performance: "
            "https://github.com/btoron/pyOFSC#migration-guide",
            DeprecationWarning,
            stacklevel=2,
        )

        # Store configuration for async client
        self._config = {
            "instance": instance,
            "client_id": client_id,
            "client_secret": client_secret,
            **kwargs,
        }

        # Event loop for async operations
        self._loop = None
        self._executor = None
        self._setup_event_loop()

        # Register cleanup
        atexit.register(self._cleanup)

        logging.debug(f"SyncOFSC initialized with config: instance={instance}")

    def _setup_event_loop(self):
        """Setup dedicated event loop for async operations."""
        try:
            # Try to create a new event loop
            self._loop = asyncio.new_event_loop()

            # Set it as the current loop for this thread
            asyncio.set_event_loop(self._loop)

            # Create thread pool executor for thread safety
            self._executor = ThreadPoolExecutor(
                max_workers=1, thread_name_prefix="ofsc-compat"
            )

            logging.debug("Event loop and thread executor created successfully")

        except Exception as e:
            logging.warning(f"Failed to create new event loop: {e}")
            # Fallback to existing loop if available
            try:
                self._loop = asyncio.get_event_loop()
                logging.debug("Using existing event loop")
            except RuntimeError:
                logging.error("No event loop available")
                raise RuntimeError(
                    "Failed to setup event loop for sync wrapper. "
                    "Consider using the async API instead."
                )

    def _cleanup(self):
        """Cleanup resources on exit."""
        try:
            if self._executor:
                self._executor.shutdown(wait=False)
                logging.debug("Thread executor shutdown")

            if self._loop and not self._loop.is_closed():
                # Cancel any pending tasks
                pending = asyncio.all_tasks(self._loop)
                for task in pending:
                    task.cancel()

                # Close the loop
                self._loop.close()
                logging.debug("Event loop closed")

        except Exception as e:
            logging.warning(f"Error during cleanup: {e}")

    def _run_async(self, coro):
        """Execute async coroutine synchronously.

        Args:
            coro: Async coroutine to execute

        Returns:
            Result of the coroutine
        """
        if self._loop is None:
            raise RuntimeError("Event loop not initialized")

        if self._loop.is_closed():
            # Recreate loop if closed
            self._setup_event_loop()

        try:
            if self._loop.is_running():
                # If loop is already running (e.g., in Jupyter), use thread executor
                if self._executor:
                    future = self._executor.submit(asyncio.run, coro)
                    return future.result(timeout=300)  # 5 minute timeout
                else:
                    raise RuntimeError(
                        "Cannot run async code in running event loop without executor"
                    )
            else:
                # Loop not running, run coroutine directly
                return self._loop.run_until_complete(coro)

        except Exception as e:
            logging.error(f"Error running async coroutine: {e}")
            raise

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._cleanup()

    def close(self):
        """Explicitly close the wrapper and cleanup resources."""
        self._cleanup()

    @property
    def core(self):
        """Get the Core API interface (v2.x compatibility).

        Returns an object that provides access to core API methods:
        - client.core.get_users()
        - client.core.get_activities()
        - etc.
        """
        if not hasattr(self, "_core_api"):
            # Create namespace object for core API
            self._core_api = type("CoreAPI", (), {})()

            # Add all core methods to the namespace
            from .method_mappings import CORE_METHODS
            from .generators import create_sync_method

            for method_name, method_config in CORE_METHODS.items():
                sync_method = create_sync_method("core", method_name, method_config)

                # Bind self to the method
                def create_bound_method(sm):
                    return lambda *args, **kwargs: sm(self, *args, **kwargs)

                bound_method = create_bound_method(sync_method)
                bound_method.__name__ = sync_method.__name__
                bound_method.__doc__ = sync_method.__doc__
                setattr(self._core_api, method_name, bound_method)

        return self._core_api

    @property
    def metadata(self):
        """Get the Metadata API interface (v2.x compatibility).

        Returns an object that provides access to metadata API methods:
        - client.metadata.get_properties()
        - client.metadata.get_workskills()
        - etc.
        """
        if not hasattr(self, "_metadata_api"):
            # Create namespace object for metadata API
            self._metadata_api = type("MetadataAPI", (), {})()

            # Add all metadata methods to the namespace
            from .method_mappings import METADATA_METHODS
            from .generators import create_sync_method

            for method_name, method_config in METADATA_METHODS.items():
                sync_method = create_sync_method("metadata", method_name, method_config)

                # Bind self to the method
                def create_bound_method(sm):
                    return lambda *args, **kwargs: sm(self, *args, **kwargs)

                bound_method = create_bound_method(sync_method)
                bound_method.__name__ = sync_method.__name__
                bound_method.__doc__ = sync_method.__doc__
                setattr(self._metadata_api, method_name, bound_method)

        return self._metadata_api

    @property
    def capacity(self):
        """Get the Capacity API interface (v2.x compatibility).

        Note: Capacity API may not be fully implemented in v3.0 yet.
        """
        if not hasattr(self, "_capacity_api"):
            # Create namespace object for capacity API
            self._capacity_api = type("CapacityAPI", (), {})()

            # Add capacity methods if available
            from .method_mappings import CAPACITY_METHODS
            from .generators import create_sync_method

            for method_name, method_config in CAPACITY_METHODS.items():
                sync_method = create_sync_method("capacity", method_name, method_config)

                # Bind self to the method
                def create_bound_method(sm):
                    return lambda *args, **kwargs: sm(self, *args, **kwargs)

                bound_method = create_bound_method(sync_method)
                bound_method.__name__ = sync_method.__name__
                bound_method.__doc__ = sync_method.__doc__
                setattr(self._capacity_api, method_name, bound_method)

        return self._capacity_api

    def __str__(self) -> str:
        """String representation of the wrapper."""
        return (
            f"OFSC(compat, instance={self._config.get('instance')}, async_backend=v3.0)"
        )

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"<OFSC compat wrapper: {self._config}>"


# Apply method mappings to create direct method access (client.get_users())
# This provides backward compatibility for the flat API structure
all_methods = get_all_methods()
for api_name, methods in all_methods.items():
    for method_name, method_config in methods.items():
        if not hasattr(OFSC, method_name):  # Avoid overriding existing methods
            from .generators import create_sync_method

            sync_method = create_sync_method(api_name, method_name, method_config)
            setattr(OFSC, method_name, sync_method)
