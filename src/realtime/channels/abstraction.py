"""channels package abstractions."""

from __future__ import annotations

from abc import ABC


class IChannel(ABC):
    """Marker base for concrete types in the ``channels`` package."""

    __slots__ = ()


__all__ = ["IChannel"]
