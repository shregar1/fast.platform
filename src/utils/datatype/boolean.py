"""Boolean coercion from strings and common scalar types."""

from __future__ import annotations

from typing import Any, FrozenSet, Optional

from .abstraction import IDatatype

__all__ = ["BooleanUtility"]

_TRUE_STR: FrozenSet[str] = frozenset(
    {"1", "true", "yes", "y", "on", "t"},
)
_FALSE_STR: FrozenSet[str] = frozenset(
    {"0", "false", "no", "n", "off", "f", ""},
)


class BooleanUtility(IDatatype):
    """Parse booleans from config flags, query params, and loose string forms."""

    @staticmethod
    def parse_optional(value: Any) -> Optional[bool]:
        """
        Return ``True``, ``False``, or ``None`` if *value* cannot be interpreted.

        - ``bool`` → unchanged.
        - ``None`` → ``None``.
        - ``int`` (non-bool): ``0`` → ``False``, ``1`` → ``True``; other ints → ``None``.
        - ``str`` (after strip, casefold): known truthy/falsey tokens → bool; else ``None``.
        - Other types → ``None``.
        """

        if isinstance(value, bool):
            return value
        if value is None:
            return None
        if isinstance(value, int) and not isinstance(value, bool):
            if value == 0:
                return False
            if value == 1:
                return True
            return None
        if isinstance(value, str):
            key = value.strip().casefold()
            if key in _TRUE_STR:
                return True
            if key in _FALSE_STR:
                return False
            return None
        return None

    @staticmethod
    def coerce(value: Any, *, default: bool = False) -> bool:
        """Like :meth:`parse_optional` but returns *default* when parsing yields ``None``."""

        parsed = BooleanUtility.parse_optional(value)
        return default if parsed is None else parsed

    @staticmethod
    def strict_bool(value: Any) -> bool:
        """
        Return a strict ``bool``.

        Raises :class:`TypeError` or :class:`ValueError` if *value* is not a clear true/false.
        """

        parsed = BooleanUtility.parse_optional(value)
        if parsed is None:
            raise ValueError(f"not a boolean-like value: {value!r}")
        return parsed
