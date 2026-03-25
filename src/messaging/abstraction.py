"""messaging package abstractions."""

from __future__ import annotations

from abc import ABC


class IMessaging(ABC):
    """Marker base for concrete types in the ``messaging`` package."""

    __slots__ = ()


__all__ = ["IMessaging"]
