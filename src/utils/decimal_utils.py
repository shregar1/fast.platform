"""Decimal and money rounding utilities.

These helpers are intentionally small and dependency-free so they can be used
across fintech, foodtech (nutrition math), and general “precise numeric”
workflows.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

__all__ = [
    "to_decimal",
    "quantize_decimal",
    "round_money",
]


def to_decimal(value: Any, *, allow_float: bool = False) -> Decimal:
    """Convert common input types to :class:`decimal.Decimal` safely.

    Notes:
    - Floats are disallowed by default because they can introduce binary
      representation artifacts. If you must pass a float, set
      ``allow_float=True``.
    """

    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        # bool is a subclass of int; refuse to avoid surprising callers.
        raise TypeError("bool cannot be converted to Decimal")
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, str):
        return Decimal(value)
    if isinstance(value, float):
        if not allow_float:
            raise TypeError(
                "float input is not allowed by default; pass a string/Decimal instead "
                "or set allow_float=True"
            )
        # Convert via string to reduce float->decimal surprise.
        return Decimal(str(value))

    raise TypeError(f"Unsupported type for Decimal conversion: {type(value).__name__}")


def quantize_decimal(
    value: Any,
    *,
    decimal_places: int,
    rounding=ROUND_HALF_UP,
    allow_float: bool = False,
) -> Decimal:
    """Quantize to a fixed number of decimal places."""

    if decimal_places < 0:
        raise ValueError("decimal_places must be >= 0")

    dec_value = to_decimal(value, allow_float=allow_float)
    quant = Decimal("1").scaleb(-decimal_places)  # 10 ** (-decimal_places)
    return dec_value.quantize(quant, rounding=rounding)


def round_money(
    amount: Any,
    *,
    minor_units: int = 2,
    rounding=ROUND_HALF_UP,
    allow_float: bool = False,
) -> Decimal:
    """Round an amount to currency minor units (e.g. cents for USD)."""

    return quantize_decimal(
        amount,
        decimal_places=minor_units,
        rounding=rounding,
        allow_float=allow_float,
    )

