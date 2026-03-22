"""
Feature flags client interface and factory.
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from typing import Any, Optional

from fast_platform import FeatureFlagsConfiguration

from .evaluation import FlagEvaluation, FlagEvaluationReason


class IFeatures(ABC):
    """Marker base for concrete types in the ``features`` package."""

    __slots__ = ()


class IFeatureFlagsClient(IFeatures, ABC):
    """Interface for feature flag clients."""

    @abstractmethod
    def is_enabled(self, flag_key: str, context: Optional[dict[str, Any]] = None) -> bool:
        """Return True if the feature flag is enabled for the given context."""
        raise NotImplementedError

    @abstractmethod
    def get_value(self, flag_key: str, context: Optional[dict[str, Any]] = None) -> Any:
        """Return the flag value (e.g. string, number, JSON)."""
        raise NotImplementedError

    def evaluate_with_reason(
        self, flag_key: str, context: Optional[dict[str, Any]] = None
    ) -> FlagEvaluation:
        """
        Return enabled state, value, and a coarse ``reason`` for debugging UIs.

        Default implementation uses :meth:`is_enabled` / :meth:`get_value` with
        :attr:`FlagEvaluationReason.DEFAULT`. Providers may override for richer reasons.
        """
        return FlagEvaluation(
            enabled=self.is_enabled(flag_key, context),
            value=self.get_value(flag_key, context),
            reason=FlagEvaluationReason.DEFAULT,
        )


def build_feature_flags_client() -> Optional[IFeatureFlagsClient]:
    """
    Build a feature flags client from FeatureFlagsConfiguration (config/feature_flags/config.json).

    Resolution order:

    1. **Snapshot** — ``FASTMVC_FEATURE_FLAGS_SNAPSHOT`` (or ``FASTMVC_FEATURE_FLAGS_SNAPSHOT_PATH``)
       env var pointing to a JSON file, or ``snapshot.enabled`` + ``snapshot.path`` in config.
    2. **LaunchDarkly** when enabled and ``sdk_key`` is set.
    3. **Unleash** when enabled and ``url`` is set.

    If **kill switch** is active (see :func:`fast_feature_flags.kill_switch.is_kill_switch_active`),
    the client is wrapped with :class:`fast_feature_flags.kill_switch.KillSwitchFeatureFlagsClient`.
    """
    from .kill_switch import (
        EmptyFeatureFlagsClient,
        KillSwitchFeatureFlagsClient,
        is_kill_switch_active,
    )

    cfg = FeatureFlagsConfiguration().get_config()

    env_snapshot = os.environ.get("FASTMVC_FEATURE_FLAGS_SNAPSHOT") or os.environ.get(
        "FASTMVC_FEATURE_FLAGS_SNAPSHOT_PATH"
    )
    snapshot_path = env_snapshot or ""
    if not snapshot_path and getattr(cfg.snapshot, "enabled", False):
        snapshot_path = getattr(cfg.snapshot, "path", "") or ""

    client: Optional[IFeatureFlagsClient] = None

    if snapshot_path:
        try:
            from .snapshot import SnapshotFeatureFlagsClient

            client = SnapshotFeatureFlagsClient.from_path(snapshot_path)
        except (OSError, ValueError, json.JSONDecodeError):
            client = None

    if client is None and getattr(cfg.launchdarkly, "enabled", False) and cfg.launchdarkly.sdk_key:
        try:
            from .launchdarkly_client import LaunchDarklyFeatureFlagsClient

            client = LaunchDarklyFeatureFlagsClient(
                sdk_key=cfg.launchdarkly.sdk_key,
                default_user_key=getattr(cfg.launchdarkly, "default_user_key", "anonymous"),
            )
        except ImportError:
            pass

    if client is None and getattr(cfg.unleash, "enabled", False) and cfg.unleash.url:
        try:
            from .unleash_client import UnleashFeatureFlagsClient

            client = UnleashFeatureFlagsClient(
                url=cfg.unleash.url,
                app_name=cfg.unleash.app_name,
                instance_id=cfg.unleash.instance_id,
                api_key=cfg.unleash.api_key,
            )
        except ImportError:
            pass

    if is_kill_switch_active():
        inner = client if client is not None else EmptyFeatureFlagsClient()
        client = KillSwitchFeatureFlagsClient(inner)

    return client
