"""
Structured flag evaluation with a ``reason`` for debugging / admin UIs.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class FlagEvaluationReason(str, Enum):
    """Why a flag resolved to its current value."""

    DEFAULT = "default"  # fallback / SDK default
    RULE = "rule"  # explicit targeting rule matched
    PERCENTAGE = "percentage"  # percentage rollout / hash bucketing
    SNAPSHOT = "snapshot"  # offline JSON snapshot
    KILL_SWITCH = "kill_switch"  # global incident override — all off
    UNKNOWN = "unknown"  # provider did not expose a reason


@dataclass(frozen=True)
class FlagEvaluation:
    """Result of :meth:`IFeatureFlagsClient.evaluate_with_reason`."""

    enabled: bool
    value: Any
    reason: FlagEvaluationReason
    detail: Optional[str] = None
