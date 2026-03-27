"""Base types for :mod:`utils.html`."""

from __future__ import annotations

from ..abstraction import IUtility


class IHtmlUtility(IUtility):
    """Marker for HTML escape / strip helpers under :mod:`utils.html`."""

    __slots__ = ()


__all__ = ["IHtmlUtility"]
