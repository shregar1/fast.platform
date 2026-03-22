"""Payments configuration loader (uses :func:`fast_platform.config.load_config_json`)."""

from typing import Optional

from fast_platform import load_config_json

from .dto import (
    LinkConfigDTO,
    PayUConfigDTO,
    PaypalConfigDTO,
    PaymentsConfigurationDTO,
    RazorpayConfigDTO,
    StripeConfigDTO,
)


class PaymentsConfiguration:
    """Singleton configuration for payment providers."""

    _instance: Optional["PaymentsConfiguration"] = None

    def __new__(cls) -> "PaymentsConfiguration":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            raw = load_config_json("payments", "PAYMENTS")
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
