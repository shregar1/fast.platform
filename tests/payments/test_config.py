"""Tests for payments configuration singleton."""

from unittest.mock import patch

from payments.config import PaymentsConfiguration


def test_payments_configuration_loads_provider_blocks():
    PaymentsConfiguration._instance = None
    raw = {
        "stripe": {"enabled": True, "api_key": "sk_test"},
        "razorpay": {"enabled": True, "key_id": "rzp_x"},
    }
    with patch("payments.config.load_config_json", return_value=raw):
        cfg = PaymentsConfiguration()
    dto = cfg.get_config()
    assert dto.stripe.enabled is True
    assert dto.stripe.api_key == "sk_test"
    assert dto.razorpay.key_id == "rzp_x"


def test_payments_configuration_defaults_when_config_missing():
    PaymentsConfiguration._instance = None
    with patch("payments.config.load_config_json", return_value=None):
        cfg = PaymentsConfiguration()
    dto = cfg.get_config()
    assert dto.stripe.enabled is False
    assert dto.paypal.environment == "sandbox"
