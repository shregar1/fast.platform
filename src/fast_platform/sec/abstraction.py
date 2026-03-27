"""sec package abstractions."""

from __future__ import annotations

from abc import ABC


class ISec(ABC):
    """Marker base for concrete types in the ``sec`` package."""

    __slots__ = ()


__all__ = ["ISec"]
