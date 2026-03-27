"""Module test_init.py."""

from __future__ import annotations

"""Smoke test package import."""
from tests.integrations.payments.abstraction import IPaymentsTests


class TestInit(IPaymentsTests):
    """Represents the TestInit class."""

    def test_import(self) -> None:
        """Execute test_import operation.

        Returns:
            The result of the operation.
        """
        import integrations.payments as p

        assert p.PaymentsConfiguration is not None
        assert p.PaymentsConfigurationDTO is not None
        assert p.CheckoutSession is not None
        assert p.IPaymentGateway is not None
