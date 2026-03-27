"""DTOs for channels/pub-sub configuration settings."""

from typing import List

from pydantic import BaseModel


class ChannelsConfigurationDTO(BaseModel):
    """DTO for channels configuration.

    Fields:
        backend (str): Backend type: "redis", "kafka", "pusher", etc.
        topics (list[str]): Default topics to use for pub/sub.
    """

    backend: str = "none"
    topics: List[str] = []
