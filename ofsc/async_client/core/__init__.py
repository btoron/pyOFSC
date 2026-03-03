"""Async OFSCore API module package.

Composes AsyncOFSCore from a base class (all non-user methods) and a users mixin.
External interface is unchanged: AsyncOFSCore exposes all methods directly.
"""

from ._base import _AsyncOFSCoreBase
from .resources import AsyncOFSCoreResourcesMixin
from .users import AsyncOFSCoreUsersMixin


class AsyncOFSCore(
    AsyncOFSCoreResourcesMixin, AsyncOFSCoreUsersMixin, _AsyncOFSCoreBase
):
    """Async version of OFSCore API module."""

    pass


__all__ = ["AsyncOFSCore"]
