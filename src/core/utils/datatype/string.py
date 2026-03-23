"""String helpers (trim, emptiness, truncation)."""

from __future__ import annotations

from typing import Optional

from .abstraction import IDatatype

__all__ = ["StringUtility"]


class StringUtility(IDatatype):
    """Small, dependency-free string operations."""

    @staticmethod
    def is_blank(value: Optional[str]) -> bool:
        """True if *value* is None or contains only whitespace."""

        if value is None:
            return True
        return len(value.strip()) == 0

    @staticmethod
    def strip_or_empty(value: Optional[str]) -> str:
        """Return stripped text, or an empty string for None."""

        if value is None:
            return ""
        return value.strip()

    @staticmethod
    def optional_strip(value: Optional[str]) -> Optional[str]:
        """Strip *value*; return ``None`` if *value* is None or becomes empty after strip."""

        if value is None:
            return None
        s = value.strip()
        return s if s else None

    @staticmethod
    def truncate(value: str, max_len: int, *, suffix: str = "...") -> str:
        """
        Shorten *value* to at most *max_len* characters, appending *suffix* when truncated.

        If *max_len* is less than or equal to ``len(suffix)``, returns *suffix* truncated to *max_len*.
        """

        if max_len <= 0:
            return ""
        if len(value) <= max_len:
            return value
        if len(suffix) >= max_len:
            return suffix[:max_len]
        return value[: max_len - len(suffix)] + suffix
