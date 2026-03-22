"""Singleton accessor for payments configuration."""

from __future__ import annotations

import json
import os
from typing import Optional

from loguru import logger

from dtos.payments import (
    LinkConfigDTO,
    PaymentsConfigurationDTO,
    PaypalConfigDTO,
    PayUConfigDTO,
    RazorpayConfigDTO,
    StripeConfigDTO,
)


def _load_config_json(section: str, env_key: str) -> Optional[dict]:
    """Load ``config/<section>/config.json`` (or ``FASTMVC_CONFIG_BASE/...``)."""
    path = os.getenv(f"FASTMVC_{env_key}_CONFIG_PATH")
    if not path:
        base = os.getenv("FASTMVC_CONFIG_BASE")
        path = (
            os.path.join(base, section, "config.json") if base else f"config/{section}/config.json"
        )
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.debug("Config file not found: %s", path)
        return None
    except json.JSONDecodeError as exc:
        logger.warning("Invalid JSON in %s: %s", path, exc)
        return None


class PaymentsConfiguration:
    """Singleton configuration for payment providers."""

    _instance: Optional["PaymentsConfiguration"] = None

    def __new__(cls) -> "PaymentsConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            raw = _load_config_json("payments", "PAYMENTS")
            r = raw or {}
            cls._instance._dto = PaymentsConfigurationDTO(
                stripe=StripeConfigDTO(**(r.get("stripe") or {})),
                razorpay=RazorpayConfigDTO(**(r.get("razorpay") or {})),
                paypal=PaypalConfigDTO(**(r.get("paypal") or {})),
                payu=PayUConfigDTO(**(r.get("payu") or {})),
                link=LinkConfigDTO(**(r.get("link") or {})),
            )
        return cls._instance

    def get_config(self) -> PaymentsConfigurationDTO:
        return self._dto
