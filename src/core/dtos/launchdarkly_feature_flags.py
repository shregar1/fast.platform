"""LaunchDarkly feature flags subsection."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class LaunchDarklyFeatureFlagsDTO(IDTO):
    """Represents the LaunchDarklyFeatureFlagsDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    sdk_key: str = ""
    default_user_key: str = "anonymous"
