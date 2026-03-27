"""providers package abstractions."""

from __future__ import annotations

from abc import ABC


class IProviders(ABC):
    """Marker base for concrete types in the ``providers`` package."""

    __slots__ = ()


__all__ = ["IProviders"]
