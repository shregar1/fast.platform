"""Singleton accessor for feature flags configuration."""

from __future__ import annotations

from typing import Optional, Type

from dtos import FeatureFlagsConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class FeatureFlagsConfiguration(ConfigurationSingletonBase[FeatureFlagsConfigurationDTO]):
    _instance: Optional["FeatureFlagsConfiguration"] = None
    _section: str = "feature_flags"
    _env_key: str = "FEATURE_FLAGS"
    _dto: Type[FeatureFlagsConfigurationDTO] = FeatureFlagsConfigurationDTO
