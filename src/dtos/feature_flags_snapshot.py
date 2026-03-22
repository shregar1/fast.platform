"""Feature flags snapshot subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class FeatureFlagsSnapshotDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    path: str = ""
