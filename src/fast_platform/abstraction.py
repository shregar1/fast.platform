"""fast_platform package abstractions."""

from __future__ import annotations

from abc import ABC


class IPlatform(ABC):
    """Marker base for concrete types in the ``fast_platform`` package."""

    __slots__ = ()


__all__ = ["IPlatform"]
