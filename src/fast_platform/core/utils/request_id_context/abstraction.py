"""Base types for :mod:`utils.request_id_context`."""

from __future__ import annotations

from ..abstraction import IUtility


class IRequestIdContextUtility(IUtility):
    """Marker for request correlation id context under :mod:`utils.request_id_context`."""

    __slots__ = ()


__all__ = ["IRequestIdContextUtility"]
