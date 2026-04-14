"""fast_platform.caching package abstractions."""

from __future__ import annotations

from abc import ABC


class ICaching(ABC):
    """Marker base for concrete types in the ``fast_platform.caching`` package."""

    __slots__ = ()


__all__ = ["ICaching"]
