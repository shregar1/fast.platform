"""Feature flags snapshot subsection."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class FeatureFlagsSnapshotDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    path: str = ""
