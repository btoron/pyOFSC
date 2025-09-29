"""Convenience import for backward compatibility wrapper.

This module provides easy access to the backward compatibility wrapper:

    from ofsc.compat import OFSC

    # Same API as v2.x
    client = OFSC(instance="demo", client_id="id", client_secret="secret")
    users = client.get_users()
"""

from .compat import OFSC

__all__ = ["OFSC"]
