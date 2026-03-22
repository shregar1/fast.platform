"""AWS SQS queue backend subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class SQSConfigDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    region: str = ""
    queue_url: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""
