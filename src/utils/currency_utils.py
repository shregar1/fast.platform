"""Currency helpers (minor/major unit conversion)."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from .decimal_utils import round_money

__all__ = [
    "currency_exponent",
    "major_to_minor",
    "minor_to_major",
]


# Common currency exponents (number of decimal places in the “major” unit).
# Most currencies use 2 minor units per major. Some use 0.
_CURRENCY_EXPONENTS: dict[str, int] = {
    "JPY": 0,
    "KRW": 0,
    "VND": 0,
    "CLP": 0,
    "IDR": 0,
}


def currency_exponent(currency_code: str) -> int:
    """Return the number of minor decimal places for a currency code."""

    if not currency_code:
        raise ValueError("currency_code is required")
    return _CURRENCY_EXPONENTS.get(currency_code.upper(), 2)


def major_to_minor(
    amount_major: Any,
    currency_code: str,
    *,
    rounding=ROUND_HALF_UP,
) -> int:
    """Convert major units to minor units.

    Example:
        major_to_minor(12.34, "USD") -> 1234
    """

    exp = currency_exponent(currency_code)
    rounded = round_money(amount_major, minor_units=exp, rounding=rounding)
    factor = Decimal("1").scaleb(exp)  # 10 ** exp
    return int((rounded * factor).to_integral_value(rounding=rounding))


def minor_to_major(
    amount_minor: int | str,
    currency_code: str,
    *,
    quantize: bool = True,
) -> Decimal:
    """Convert minor integer units to major decimal units."""

    exp = currency_exponent(currency_code)
    dec_minor = Decimal(str(amount_minor))
    factor = Decimal("1").scaleb(exp)  # 10 ** exp
    major = dec_minor / factor
    if quantize:
        # Quantize to the currency’s exponent for stable formatting/comparisons.
        major = major.quantize(Decimal("1").scaleb(-exp))
    return major

