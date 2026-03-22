"""AWS secrets subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class AwsSecretsDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    region: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""
    prefix: str = ""
