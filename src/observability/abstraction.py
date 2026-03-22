"""observability package abstractions."""

from __future__ import annotations

from abc import ABC


class IObservability(ABC):
    """Marker base for concrete types in the ``observability`` package."""

    __slots__ = ()


__all__ = ["IObservability"]
