"""integrations package abstractions."""

from __future__ import annotations

from abc import ABC


class IIntegrations(ABC):
    """Marker base for concrete types in the ``integrations`` package."""

    __slots__ = ()


__all__ = ["IIntegrations"]
