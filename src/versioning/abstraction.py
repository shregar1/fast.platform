"""versioning package abstractions."""

from __future__ import annotations

from abc import ABC


class IVersioning(ABC):
    """Marker base for concrete types in the ``versioning`` package."""

    __slots__ = ()


__all__ = ["IVersioning"]
