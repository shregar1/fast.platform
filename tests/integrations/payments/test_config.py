"""Module test_config.py."""

from __future__ import annotations

"""Tests for payments configuration singleton."""
from unittest.mock import patch

from fast_platform.core.configuration.payments import PaymentsConfiguration
from tests.integrations.payments.abstraction import IPaymentsTests


class TestConfig(IPaymentsTests):
    """Represents the TestConfig class."""

    def test_payments_configuration_loads_provider_blocks(self) -> None:
        """Execute test_payments_configuration_loads_provider_blocks operation.

        Returns:
            The result of the operation.
        """
        PaymentsConfiguration._instance = None
        raw = {
            "stripe": {"enabled": True, "api_key": "sk_test"},
            "razorpay": {"enabled": True, "key_id": "rzp_x"},
        }
        with patch.object(PaymentsConfiguration, "load_config_json", return_value=raw):
            cfg = PaymentsConfiguration()
        dto = cfg.get_config()
        assert dto.stripe.enabled is True
        assert dto.stripe.api_key == "sk_test"
        assert dto.razorpay.key_id == "rzp_x"

    def test_payments_configuration_defaults_when_config_missing(self) -> None:
        """Execute test_payments_configuration_defaults_when_config_missing operation.

        Returns:
            The result of the operation.
        """
        PaymentsConfiguration._instance = None
        with patch.object(PaymentsConfiguration, "load_config_json", return_value=None):
            cfg = PaymentsConfiguration()
        dto = cfg.get_config()
        assert dto.stripe.enabled is False
        assert dto.paypal.environment == "sandbox"
