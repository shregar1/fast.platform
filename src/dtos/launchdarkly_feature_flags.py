"""LaunchDarkly feature flags subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class LaunchDarklyFeatureFlagsDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    sdk_key: str = ""
    default_user_key: str = "anonymous"
