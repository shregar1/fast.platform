"""
Push notification configuration loader.

Reads from config/push/config.json (or FASTMVC_PUSH_CONFIG_PATH).
"""

import json
import os
from typing import Optional

from loguru import logger

from dtos.notifications import APNSConfigDTO, FCMConfigDTO, PushConfigurationDTO


class NotificationsConfiguration:
    """Configuration manager for push notification settings."""

    _instance: Optional["NotificationsConfiguration"] = None

    def __new__(cls) -> "NotificationsConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = {}
            cls._instance.load_config()
        return cls._instance

    def load_config(self) -> None:
        path = os.getenv("FASTMVC_PUSH_CONFIG_PATH", "config/push/config.json")
        cfg: dict = {}
        try:
            with open(path) as f:
                cfg = json.load(f)
            logger.debug("Push notification config loaded successfully.")
        except FileNotFoundError:
            logger.debug("Push notification config file not found.")
        except json.JSONDecodeError:
            logger.debug("Error decoding push notification config file.")

        apns_cfg = cfg.setdefault("apns", {})
        if (v := os.getenv("APNS_ENABLED")) is not None:
            apns_cfg["enabled"] = v.strip().lower() in {"1", "true", "yes", "on"}
        if (v := os.getenv("APNS_KEY_ID")) is not None:
            apns_cfg["key_id"] = v
        if (v := os.getenv("APNS_TEAM_ID")) is not None:
            apns_cfg["team_id"] = v
        if (v := os.getenv("APNS_BUNDLE_ID")) is not None:
            apns_cfg["bundle_id"] = v
        if (v := os.getenv("APNS_PRIVATE_KEY_PATH")) is not None:
            apns_cfg["private_key_path"] = v
        if (v := os.getenv("APNS_USE_SANDBOX")) is not None:
            apns_cfg["use_sandbox"] = v.strip().lower() in {"1", "true", "yes", "on"}

        fcm_cfg = cfg.setdefault("fcm", {})
        if (v := os.getenv("FCM_ENABLED")) is not None:
            fcm_cfg["enabled"] = v.strip().lower() in {"1", "true", "yes", "on"}
        if (v := os.getenv("FCM_SERVER_KEY")) is not None:
            fcm_cfg["server_key"] = v
        if (v := os.getenv("FCM_PROJECT_ID")) is not None:
            fcm_cfg["project_id"] = v

        self.config = cfg

    def get_config(self) -> PushConfigurationDTO:
        cfg = self.config
        return PushConfigurationDTO(
            apns=APNSConfigDTO(**(cfg.get("apns") or {})),
            fcm=FCMConfigDTO(**(cfg.get("fcm") or {})),
        )
