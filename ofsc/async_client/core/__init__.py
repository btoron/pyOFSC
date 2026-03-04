"""Async OFSCore API module package.

Composes AsyncOFSCore from a base class and mixins for resources, users, and inventories.
External interface is unchanged: AsyncOFSCore exposes all methods directly.
"""

from ._base import _AsyncOFSCoreBase
from .inventories import AsyncOFSCoreInventoriesMixin
from .resources import AsyncOFSCoreResourcesMixin
from .users import AsyncOFSCoreUsersMixin


class AsyncOFSCore(
    AsyncOFSCoreInventoriesMixin,
    AsyncOFSCoreResourcesMixin,
    AsyncOFSCoreUsersMixin,
    _AsyncOFSCoreBase,
):
    """Async version of OFSCore API module."""

    pass


__all__ = ["AsyncOFSCore"]
