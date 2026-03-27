"""Base types for :mod:`core.utils.crowdfunding`."""

from __future__ import annotations

from core.utils.abstraction import IUtility


class ICrowdfundingUtility(IUtility):
    """Marker for pure crowdfunding helpers (funding math, slug rules)."""

    __slots__ = ()


__all__ = ["ICrowdfundingUtility"]
