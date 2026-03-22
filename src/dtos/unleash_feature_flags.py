"""Unleash feature flags subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class UnleashFeatureFlagsDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    url: str = ""
    app_name: str = ""
    instance_id: str = ""
    api_key: str = ""
