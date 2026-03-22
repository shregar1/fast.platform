"""Nutrition math utilities (foodtech-friendly).

These are intentionally simple so they can be used for:
- calorie calculations from macros
- quick “kcal from grams” conversions
"""

from __future__ import annotations

from typing import Union

__all__ = ["kcal_from_macros"]


Number = Union[int, float]


def kcal_from_macros(*, carbs_g: Number = 0, protein_g: Number = 0, fat_g: Number = 0) -> float:
    """Compute calories from macro grams.

    Uses standard factors:
    - carbs: 4 kcal/g
    - protein: 4 kcal/g
    - fat: 9 kcal/g
    """

    return (float(carbs_g) * 4.0) + (float(protein_g) * 4.0) + (float(fat_g) * 9.0)

