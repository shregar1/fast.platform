"""admin package abstractions."""

from __future__ import annotations

from abc import ABC


class IAdmin(ABC):
    """Marker base for concrete types in the ``admin`` package."""

    __slots__ = ()


__all__ = ["IAdmin"]
