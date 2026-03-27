"""Crowdfunding helpers (funding progress, slug normalization, tier matching).

Stateless utilities for backend services; persistence lives in ``fast-database`` models/repos.
"""

from __future__ import annotations

import re
from decimal import ROUND_DOWN, Decimal

from .abstraction import ICrowdfundingUtility

_SLUG_RE = re.compile(r"[^a-z0-9]+")


class CrowdfundingUtility(ICrowdfundingUtility):
    """Percent funded, remaining goal, slug normalization, reward minimum checks."""

    @staticmethod
    def percent_funded(funded_cents: int, goal_cents: int) -> float:
        """Return funding progress in ``[0.0, 100.0]``.

        If ``goal_cents`` is zero or negative, returns ``0.0`` (avoid divide-by-zero).
        """
        if goal_cents <= 0:
            return 0.0
        ratio = (Decimal(funded_cents) / Decimal(goal_cents)) * Decimal(100)
        return float(ratio.quantize(Decimal("0.01"), rounding=ROUND_DOWN))

    @staticmethod
    def remaining_goal_cents(funded_cents: int, goal_cents: int) -> int:
        """Amount still needed to reach the goal, floored at zero."""
        return max(0, int(goal_cents) - int(funded_cents))

    @staticmethod
    def is_goal_met(funded_cents: int, goal_cents: int) -> bool:
        """Execute is_goal_met operation.

        Args:
            funded_cents: The funded_cents parameter.
            goal_cents: The goal_cents parameter.

        Returns:
            The result of the operation.
        """
        return int(funded_cents) >= int(goal_cents) and int(goal_cents) > 0

    @staticmethod
    def normalize_campaign_slug(raw: str) -> str:
        """Lowercase URL slug: alphanumerics and hyphens, collapsed and stripped.

        Empty input yields ``"project"`` as a safe fallback.
        """
        s = (raw or "").strip().lower()
        s = _SLUG_RE.sub("-", s).strip("-")
        return s if s else "project"

    @staticmethod
    def pledge_covers_reward(pledge_amount_cents: int, reward_minimum_cents: int) -> bool:
        """True if the pledge meets or exceeds the reward tier minimum."""
        return int(pledge_amount_cents) >= int(reward_minimum_cents)


__all__ = ["CrowdfundingUtility", "ICrowdfundingUtility"]
