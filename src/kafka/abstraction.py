"""kafka package abstractions."""

from __future__ import annotations

from abc import ABC


class IKafka(ABC):
    """Marker base for concrete types in the ``kafka`` package."""

    __slots__ = ()


__all__ = ["IKafka"]
