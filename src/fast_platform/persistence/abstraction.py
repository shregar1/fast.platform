"""persistence package abstractions."""

from __future__ import annotations

from abc import ABC


class IPersistence(ABC):
    """Marker base for concrete types in the ``persistence`` package."""

    __slots__ = ()


__all__ = ["IPersistence"]
