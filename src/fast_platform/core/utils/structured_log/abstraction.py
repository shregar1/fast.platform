"""Base types for :mod:`utils.structured_log`."""

from __future__ import annotations

from ..abstraction import IUtility


class IStructuredLogUtility(IUtility):
    """Marker for JSON-friendly log record builders under :mod:`utils.structured_log`."""

    __slots__ = ()


__all__ = ["IStructuredLogUtility"]
