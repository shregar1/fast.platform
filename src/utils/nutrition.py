"""Nutrition math utilities (foodtech-friendly)."""

from __future__ import annotations

from typing import Union

__all__ = ["NutritionUtility"]

Number = Union[int, float]


class NutritionUtility:
    """Calorie calculations from macro grams."""

    @staticmethod
    def kcal_from_macros(*, carbs_g: Number = 0, protein_g: Number = 0, fat_g: Number = 0) -> float:
        """Compute calories from macro grams (4/4/9 kcal per g)."""

        return (float(carbs_g) * 4.0) + (float(protein_g) * 4.0) + (float(fat_g) * 9.0)
