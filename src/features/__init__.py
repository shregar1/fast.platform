"""
fast_feature_flags – Feature flags (LaunchDarkly, Unleash) for FastMVC.
"""

from fast_platform import FeatureFlagsConfiguration, FeatureFlagsConfigurationDTO

from .base import IFeatureFlagsClient, build_feature_flags_client
from .evaluation import FlagEvaluation, FlagEvaluationReason
from .kill_switch import EmptyFeatureFlagsClient, KillSwitchFeatureFlagsClient, is_kill_switch_active
from .request_context import feature_flags_context_from_request
from .snapshot import SnapshotFeatureFlagsClient, load_snapshot_from_path
from .streaming import format_sse_event, poll_snapshot_changes, snapshot_sse_generator

__version__ = "0.3.0"

__all__ = [
    "EmptyFeatureFlagsClient",
    "FlagEvaluation",
    "FlagEvaluationReason",
    "FeatureFlagsConfiguration",
    "FeatureFlagsConfigurationDTO",
    "IFeatureFlagsClient",
    "KillSwitchFeatureFlagsClient",
    "SnapshotFeatureFlagsClient",
    "build_feature_flags_client",
    "feature_flags_context_from_request",
    "format_sse_event",
    "is_kill_switch_active",
    "load_snapshot_from_path",
    "poll_snapshot_changes",
    "snapshot_sse_generator",
]
