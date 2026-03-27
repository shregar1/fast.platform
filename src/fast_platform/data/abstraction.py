"""data package abstractions."""

from __future__ import annotations

from abc import ABC


class IDataPlatform(ABC):
    """Marker base for concrete types in the ``data`` package."""

    __slots__ = ()


__all__ = ["IDataPlatform"]
