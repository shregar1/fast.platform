"""GCP secrets subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class GcpSecretsDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    project_id: str = ""
    credentials_json_path: str = ""
