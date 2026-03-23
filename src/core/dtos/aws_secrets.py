"""AWS secrets subsection."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class AwsSecretsDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    region: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""
    prefix: str = ""
