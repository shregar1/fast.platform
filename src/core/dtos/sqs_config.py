"""AWS SQS queue backend subsection."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class SQSConfigDTO(IDTO):
    """Represents the SQSConfigDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    region: str = ""
    queue_url: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""
