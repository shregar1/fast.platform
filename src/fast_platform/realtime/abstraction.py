"""realtime package abstractions."""

from __future__ import annotations

from abc import ABC


class IRealtime(ABC):
    """Marker base for concrete types in the ``realtime`` package."""

    __slots__ = ()


__all__ = ["IRealtime"]
