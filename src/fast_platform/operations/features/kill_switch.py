"""Global incident mode: force all flags off via environment or marker file."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

from .abstraction import IFeatureFlagsClient
from .evaluation import FlagEvaluation, FlagEvaluationReason


class EmptyFeatureFlagsClient(IFeatureFlagsClient):
    """All flags off; used as inner client when kill switch is on but no backend is configured."""

    def is_enabled(self, flag_key: str, context: Optional[dict[str, Any]] = None) -> bool:
        """Execute is_enabled operation.

        Args:
            flag_key: The flag_key parameter.
            context: The context parameter.

        Returns:
            The result of the operation.
        """
        return False

    def get_value(self, flag_key: str, context: Optional[dict[str, Any]] = None) -> Any:
        """Execute get_value operation.

        Args:
            flag_key: The flag_key parameter.
            context: The context parameter.

        Returns:
            The result of the operation.
        """
        return None


# Any truthy value enables kill switch (1, true, yes, on).
_ENV_KEYS = (
    "FASTMVC_FEATURE_FLAGS_KILL_SWITCH",
    "FASTMVC_KILL_ALL_FLAGS",
    "FASTMVC_FEATURE_FLAGS_INCIDENT_MODE",
)

_FILE_ENV_KEYS = (
    "FASTMVC_FEATURE_FLAGS_KILL_SWITCH_FILE",
    "FASTMVC_KILL_SWITCH_FILE",
)


def is_kill_switch_active() -> bool:
    """Return True when kill switch is enabled:

    - Env: ``FASTMVC_FEATURE_FLAGS_KILL_SWITCH``, ``FASTMVC_KILL_ALL_FLAGS``, or
      ``FASTMVC_FEATURE_FLAGS_INCIDENT_MODE`` set to a truthy string; **or**
    - File: path from ``FASTMVC_FEATURE_FLAGS_KILL_SWITCH_FILE`` (or ``FASTMVC_KILL_SWITCH_FILE``)
      points to an **existing** file (empty marker file is enough).
    """
    for ek in _ENV_KEYS:
        v = os.environ.get(ek)
        if v is not None and str(v).strip().lower() in {"1", "true", "yes", "on"}:
            return True

    for fk in _FILE_ENV_KEYS:
        p = os.environ.get(fk)
        if p and Path(p).is_file():
            return True

    return False


class KillSwitchFeatureFlagsClient(IFeatureFlagsClient):
    """Wraps an inner client but forces every flag off with ``reason=kill_switch``."""

    def __init__(self, inner: IFeatureFlagsClient) -> None:
        """Execute __init__ operation.

        Args:
            inner: The inner parameter.
        """
        self._inner = inner

    def is_enabled(self, flag_key: str, context: Optional[dict[str, Any]] = None) -> bool:
        """Execute is_enabled operation.

        Args:
            flag_key: The flag_key parameter.
            context: The context parameter.

        Returns:
            The result of the operation.
        """
        return False

    def get_value(self, flag_key: str, context: Optional[dict[str, Any]] = None) -> Any:
        """Execute get_value operation.

        Args:
            flag_key: The flag_key parameter.
            context: The context parameter.

        Returns:
            The result of the operation.
        """
        return None

    def evaluate_with_reason(
        self, flag_key: str, context: Optional[dict[str, Any]] = None
    ) -> FlagEvaluation:
        """Execute evaluate_with_reason operation.

        Args:
            flag_key: The flag_key parameter.
            context: The context parameter.

        Returns:
            The result of the operation.
        """
        return FlagEvaluation(
            enabled=False,
            value=None,
            reason=FlagEvaluationReason.KILL_SWITCH,
            detail="global_kill_switch",
        )
