"""WebRTC configuration loader.

Reads from config/webrtc/config.json (or FASTMVC_WEBRTC_CONFIG_PATH).
"""

import json
import os
from typing import Optional

from loguru import logger

from .dto import WebRTCConfigurationDTO


class WebRTCConfiguration:
    """Configuration manager for WebRTC signaling settings."""

    _instance: Optional["WebRTCConfiguration"] = None

    def __new__(cls) -> "WebRTCConfiguration":
        """Execute __new__ operation.

        Returns:
            The result of the operation.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = {}
            cls._instance.load_config()
        return cls._instance

    def load_config(self) -> None:
        """Execute load_config operation.

        Returns:
            The result of the operation.
        """
        path = os.getenv("FASTMVC_WEBRTC_CONFIG_PATH")
        if not path:
            base = os.getenv("FASTMVC_CONFIG_BASE")
            path = (
                os.path.join(base, "webrtc", "config.json") if base else "config/webrtc/config.json"
            )
        try:
            with open(path) as f:
                self.config = json.load(f)
            logger.debug("WebRTC config loaded successfully.")
        except FileNotFoundError:
            logger.debug("WebRTC config file not found.")
            self.config = {}
        except json.JSONDecodeError:
            logger.debug("Error decoding WebRTC config file.")
            self.config = {}

    def get_config(self) -> WebRTCConfigurationDTO:
        """Execute get_config operation.

        Returns:
            The result of the operation.
        """
        return WebRTCConfigurationDTO(
            enabled=bool(self.config.get("enabled", False)),
            stun_servers=self.config.get("stun_servers", []),
            turn_servers=self.config.get("turn_servers", []),
            max_peers_per_room=self.config.get("max_peers_per_room", 8),
        )
