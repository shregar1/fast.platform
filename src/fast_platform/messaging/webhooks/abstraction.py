"""webhooks package abstractions."""

from __future__ import annotations

from abc import ABC


class IWebhook(ABC):
    """Marker base for concrete types in the ``webhooks`` package."""

    __slots__ = ()


__all__ = ["IWebhook"]
