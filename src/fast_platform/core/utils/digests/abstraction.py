"""Base types for :mod:`utils.digests`."""

from __future__ import annotations

from ..abstraction import IUtility


class IDigestsUtility(IUtility):
    """Marker for SHA-256 / Fernet key digest helpers under :mod:`utils.digests`."""

    __slots__ = ()


__all__ = ["IDigestsUtility"]
