"""AWS SNS events subsection."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class SnsNotificationDTO(IDTO):
    """Represents the SnsNotificationDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    region: str = ""
    topic_arn: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""
