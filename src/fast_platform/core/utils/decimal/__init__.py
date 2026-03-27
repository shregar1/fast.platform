"""Decimal and money rounding utilities."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Union

from .abstraction import IDecimalUtility

__all__ = ["DecimalUtility", "IDecimalUtility"]


class DecimalUtility(IDecimalUtility):
    """Conversion, quantization, and money rounding."""

    @staticmethod
    def to_decimal(value: Any, *, allow_float: bool = False) -> Decimal:
        """Convert common input types to :class:`decimal.Decimal` safely."""
        if isinstance(value, Decimal):
            return value
        if isinstance(value, bool):
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
            return Decimal(str(value))

        raise TypeError(f"Unsupported type for Decimal conversion: {type(value).__name__}")

    @staticmethod
    def quantize_decimal(
        value: Any,
        *,
        decimal_places: int,
        rounding: Union[str, Decimal] = ROUND_HALF_UP,
        allow_float: bool = False,
    ) -> Decimal:
        """Quantize to a fixed number of decimal places."""
        if decimal_places < 0:
            raise ValueError("decimal_places must be >= 0")

        dec_value = DecimalUtility.to_decimal(value, allow_float=allow_float)
        quant = Decimal("1").scaleb(-decimal_places)
        return dec_value.quantize(quant, rounding=rounding)

    @staticmethod
    def round_money(
        amount: Any,
        *,
        minor_units: int = 2,
        rounding: Union[str, Decimal] = ROUND_HALF_UP,
        allow_float: bool = False,
    ) -> Decimal:
        """Round an amount to currency minor units (e.g. cents for USD)."""
        return DecimalUtility.quantize_decimal(
            amount,
            decimal_places=minor_units,
            rounding=rounding,
            allow_float=allow_float,
        )
