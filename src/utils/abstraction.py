"""
Base types for :mod:`utils`.

Concrete helpers in this package inherit :class:`IUtility` so call sites and
documentation can treat them as a consistent “utility” family, even though most
implementations use only static methods and carry no instance state.
"""

from __future__ import annotations

from abc import ABC


class IUtility(ABC):
    """
    Marker abstract base for utility classes under :mod:`utils`.

    Subclasses are typically collections of :func:`staticmethod` helpers (no shared
    mutable state). Inheriting from :class:`IUtility` documents intent and keeps
    typing / discovery consistent; it does not enforce a particular method set.
    """

    pass


__all__ = ["IUtility"]
