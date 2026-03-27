"""Currency helpers (minor/major unit conversion)."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Union

from core.utils.decimal import DecimalUtility

from .abstraction import ICurrencyUtility

__all__ = ["CurrencyUtility", "ICurrencyUtility"]

_CURRENCY_EXPONENTS: dict[str, int] = {
    "JPY": 0,
    "KRW": 0,
    "VND": 0,
    "CLP": 0,
    "IDR": 0,
}


class CurrencyUtility(ICurrencyUtility):
    """Major/minor conversion using :class:`~core.utils.decimal.DecimalUtility`."""

    @staticmethod
    def currency_exponent(currency_code: str) -> int:
        """Return the number of minor decimal places for a currency code."""
        if not currency_code:
            raise ValueError("currency_code is required")
        return _CURRENCY_EXPONENTS.get(currency_code.upper(), 2)

    @staticmethod
    def major_to_minor(
        amount_major: Any,
        currency_code: str,
        *,
        rounding: Union[str, Decimal] = ROUND_HALF_UP,
    ) -> int:
        """Convert major units to minor units (e.g. ``12.34`` USD -> ``1234``)."""
        exp = CurrencyUtility.currency_exponent(currency_code)
        rounded = DecimalUtility.round_money(amount_major, minor_units=exp, rounding=rounding)
        factor = Decimal("1").scaleb(exp)
        return int((rounded * factor).to_integral_value(rounding=rounding))

    @staticmethod
    def minor_to_major(
        amount_minor: int | str,
        currency_code: str,
        *,
        quantize: bool = True,
    ) -> Decimal:
        """Convert minor integer units to major decimal units."""
        exp = CurrencyUtility.currency_exponent(currency_code)
        dec_minor = Decimal(str(amount_minor))
        factor = Decimal("1").scaleb(exp)
        major = dec_minor / factor
        if quantize:
            major = major.quantize(Decimal("1").scaleb(-exp))
        return major
