"""src package abstractions."""

from __future__ import annotations

from abc import ABC


class ISource(ABC):
    """Marker base for concrete types in the ``src`` package."""

    __slots__ = ()


__all__ = ["ISource"]
