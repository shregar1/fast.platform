"""
User notification preferences (e.g. muted categories / preference center).
"""

from __future__ import annotations

from typing import Mapping, Protocol, Set, runtime_checkable


@runtime_checkable
class INotificationPreferenceStore(Protocol):
    """Return whether *category* is muted for *user_id* (no fan-out to that user)."""

    async def is_category_muted(self, user_id: str, category: str) -> bool: ...


class AllowAllNotificationPreferences:
    """Default: nothing is muted."""

    async def is_category_muted(self, user_id: str, category: str) -> bool:
        return False


class StaticMutedCategories:
    """
    Fixed mapping ``user_id`` → set of muted category ids (e.g. ``{"marketing", "digest"}``).
    """

    def __init__(self, muted: Mapping[str, Set[str]]) -> None:
        self._muted = {uid: set(cats) for uid, cats in muted.items()}

    async def is_category_muted(self, user_id: str, category: str) -> bool:
        cats = self._muted.get(user_id)
        if not cats:
            return False
        return category in cats
