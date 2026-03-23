"""Integer parsing and bounds helpers."""

from __future__ import annotations

from typing import Any, Optional, Union

from .abstraction import IDatatype

__all__ = ["IntegerUtility"]


class IntegerUtility(IDatatype):
    """Parse integers safely; reject bool (treat like :class:`DecimalUtility`)."""

    @staticmethod
    def clamp(value: int, low: int, high: int) -> int:
        """Return *value* limited to the inclusive ``[low, high]`` range."""

        if low > high:
            raise ValueError("low must be <= high")
        return max(low, min(high, value))

    @staticmethod
    def to_int(value: Any, *, default: Optional[int] = None) -> Optional[int]:
        """
        Convert *value* to ``int``.

        - ``bool`` is rejected (use explicit ``int(bool)`` if intended).
        - ``int`` passes through.
        - ``str`` is parsed with base 10 after strip; empty or invalid → *default*.
        - ``float`` is accepted only if it is a whole number (e.g. ``3.0``); otherwise *default*.
        - Other types → *default*.
        """

        if isinstance(value, bool):
            return default
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            if value.is_integer():
                return int(value)
            return default
        if isinstance(value, str):
            s = value.strip()
            if not s:
                return default
            try:
                return int(s, 10)
            except ValueError:
                return default
        return default

    @staticmethod
    def parse_int_strict(value: Union[str, int], *, base: int = 10) -> int:
        """
        Parse an integer string (or pass through ``int``). Raises :class:`ValueError` on failure.

        *base* is passed to ``int(..., base)`` for string inputs.
        """

        if isinstance(value, bool):
            raise TypeError("bool is not accepted; use an explicit int")
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            s = value.strip()
            if not s:
                raise ValueError("empty string")
            return int(s, base)
        raise TypeError(f"expected str or int, got {type(value).__name__}")
