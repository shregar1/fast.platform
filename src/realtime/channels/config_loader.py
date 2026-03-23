"""
Channels configuration loader.

Reads from config/channels/config.json (or FASTMVC_CHANNELS_CONFIG_PATH).
"""

import json
import os
from typing import Optional

from loguru import logger

from .dto import ChannelsConfigurationDTO


class ChannelsConfiguration:
    """Configuration manager for channels (pub-sub) settings."""

    _instance: Optional["ChannelsConfiguration"] = None

    def __new__(cls) -> "ChannelsConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = {}
            cls._instance.load_config()
        return cls._instance

    def load_config(self) -> None:
        path = os.getenv("FASTMVC_CHANNELS_CONFIG_PATH")
        if not path:
            base = os.getenv("FASTMVC_CONFIG_BASE")
            path = (
                os.path.join(base, "channels", "config.json")
                if base
                else "config/channels/config.json"
            )
        try:
            with open(path) as f:
                self.config = json.load(f)
            logger.debug("Channels config loaded successfully.")
        except FileNotFoundError:
            logger.debug("Channels config file not found.")
            self.config = {}
        except json.JSONDecodeError:
            logger.debug("Error decoding channels config file.")
            self.config = {}

    def get_config(self) -> ChannelsConfigurationDTO:
        return ChannelsConfigurationDTO(
            backend=self.config.get("backend", "none"),
            topics=self.config.get("topics", []),
        )
