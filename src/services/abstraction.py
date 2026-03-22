"""Base types for :mod:`services`."""

from __future__ import annotations

from abc import ABC


class IService(ABC):
    """Base class for application services in this package."""

    __slots__ = ()


__all__ = ["IService"]
