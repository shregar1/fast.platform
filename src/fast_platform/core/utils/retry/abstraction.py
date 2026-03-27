"""Base types for :mod:`utils.retry`."""

from __future__ import annotations

from ..abstraction import IUtility


class IAsyncRetryUtility(IUtility):
    """Marker for async retry / backoff helpers under :mod:`utils.retry`."""

    __slots__ = ()


__all__ = ["IAsyncRetryUtility"]
