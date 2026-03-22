"""otel package abstractions."""

from __future__ import annotations

from abc import ABC


class IOtel(ABC):
    """Marker base for concrete types in the ``otel`` package."""

    __slots__ = ()


__all__ = ["IOtel"]
