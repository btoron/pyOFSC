"""Async OFSCore API module package.

Composes AsyncOFSCore from a base class and mixins for resources, service requests, users, and inventories.
External interface is unchanged: AsyncOFSCore exposes all methods directly.
"""

from ._base import _AsyncOFSCoreBase
from .inventories import AsyncOFSCoreInventoriesMixin
from .resources import AsyncOFSCoreResourcesMixin
from .service_requests import AsyncOFSCoreServiceRequestsMixin
from .users import AsyncOFSCoreUsersMixin


class AsyncOFSCore(
    AsyncOFSCoreInventoriesMixin,
    AsyncOFSCoreResourcesMixin,
    AsyncOFSCoreServiceRequestsMixin,
    AsyncOFSCoreUsersMixin,
    _AsyncOFSCoreBase,
):
    """Async version of OFSCore API module."""

    pass


__all__ = ["AsyncOFSCore"]
