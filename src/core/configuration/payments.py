"""Singleton accessor for payments configuration."""

from __future__ import annotations

from typing import Optional

from core.configuration.abstraction import ConfigurationSingletonBase
from core.dtos.payments import PaymentsConfigurationDTO


class PaymentsConfiguration(ConfigurationSingletonBase[PaymentsConfigurationDTO]):
    """
    Singleton configuration for payment providers.

    Reads from ``config/payments/config.json``
    (or ``FASTMVC_PAYMENTS_CONFIG_PATH`` / ``FASTMVC_CONFIG_BASE`` env vars).

    Uses :class:`~core.configuration.abstraction.ConfigurationSingletonBase`
    for the singleton pattern, JSON loading, and Pydantic validation —
    eliminating the previously hand-rolled duplicate implementation.

    Example:
        >>> cfg = PaymentsConfiguration().get_config()
        >>> cfg.stripe.enabled
        False
    """

    _instance: Optional["PaymentsConfiguration"] = None
    _section = "payments"
    _env_key = "PAYMENTS"
    _dto = PaymentsConfigurationDTO

    def get_config(self) -> PaymentsConfigurationDTO:
        """Return the validated payments configuration DTO."""
        return self._dto  # type: ignore[return-value]
