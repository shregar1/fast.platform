"""Aggregate feature flags configuration DTO."""

from __future__ import annotations

from pydantic import ConfigDict, Field

from .abstraction import IDTO
from .feature_flags_snapshot import FeatureFlagsSnapshotDTO
from .launchdarkly_feature_flags import LaunchDarklyFeatureFlagsDTO
from .unleash_feature_flags import UnleashFeatureFlagsDTO


class FeatureFlagsConfigurationDTO(IDTO):
    """Represents the FeatureFlagsConfigurationDTO class."""

    model_config = ConfigDict(extra="ignore")
    snapshot: FeatureFlagsSnapshotDTO = Field(default_factory=FeatureFlagsSnapshotDTO)
    launchdarkly: LaunchDarklyFeatureFlagsDTO = Field(default_factory=LaunchDarklyFeatureFlagsDTO)
    unleash: UnleashFeatureFlagsDTO = Field(default_factory=UnleashFeatureFlagsDTO)
