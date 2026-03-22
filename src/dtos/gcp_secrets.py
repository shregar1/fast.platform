"""GCP secrets subsection."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class GcpSecretsDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    project_id: str = ""
    credentials_json_path: str = ""
