"""AWS SNS events subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class SnsNotificationDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    region: str = ""
    topic_arn: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""
