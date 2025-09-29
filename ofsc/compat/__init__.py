"""Backward compatibility layer for OFSC v3.0.

This module provides a synchronous wrapper over the new async-only v3.0 architecture,
allowing existing v2.x code to work with minimal changes.

Usage:
    from ofsc.compat import OFSC

    # Same API as v2.x
    client = OFSC(instance="demo", client_id="id", client_secret="secret")
    users = client.get_users()  # Returns UserListResponse (same as async API)
"""

from .wrapper import OFSC

__all__ = ["OFSC"]
