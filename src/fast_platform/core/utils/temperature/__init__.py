"""Temperature conversion and unit rounding utilities."""

from __future__ import annotations

from typing import Union
from decimal import Decimal, ROUND_HALF_UP

from .abstraction import ITemperatureUtility


class TemperatureUtility(ITemperatureUtility):
    """Stateless helpers for Celsius, Fahrenheit, and Kelvin conversions."""

    @staticmethod
    def c_to_f(celsius: Union[float, int, Decimal]) -> Decimal:
        """Convert Celsius to Fahrenheit."""
        return (Decimal(str(celsius)) * Decimal("1.8")) + Decimal("32")

    @staticmethod
    def f_to_c(fahrenheit: Union[float, int, Decimal]) -> Decimal:
        """Convert Fahrenheit to Celsius."""
        return (Decimal(str(fahrenheit)) - Decimal("32")) / Decimal("1.8")

    @staticmethod
    def c_to_k(celsius: Union[float, int, Decimal]) -> Decimal:
        """Convert Celsius to Kelvin."""
        return Decimal(str(celsius)) + Decimal("273.15")

    @staticmethod
    def k_to_c(kelvin: Union[float, int, Decimal]) -> Decimal:
        """Convert Kelvin to Celsius."""
        return Decimal(str(kelvin)) - Decimal("273.15")

    @staticmethod
    def f_to_k(fahrenheit: Union[float, int, Decimal]) -> Decimal:
        """Convert Fahrenheit to Kelvin."""
        return TemperatureUtility.c_to_k(TemperatureUtility.f_to_c(fahrenheit))

    @staticmethod
    def k_to_f(kelvin: Union[float, int, Decimal]) -> Decimal:
        """Convert Kelvin to Fahrenheit."""
        return TemperatureUtility.c_to_f(TemperatureUtility.k_to_c(kelvin))

    @staticmethod
    def format_temp(
        value: Union[float, int, Decimal],
        *,
        decimal_places: int = 2,
    ) -> Decimal:
        """Round temperature to a fixed precision."""
        quant = Decimal("1").scaleb(-decimal_places)
        return Decimal(str(value)).quantize(quant, rounding=ROUND_HALF_UP)


__all__ = ["TemperatureUtility", "ITemperatureUtility"]
