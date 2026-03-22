from __future__ import annotations
"""Smoke test package import."""
from tests.integrations.payments.abstraction import IPaymentsTests




class TestInit(IPaymentsTests):
    def test_import(self) -> None:
        import payments as p

        assert p.PaymentsConfiguration is not None
        assert p.PaymentsConfigurationDTO is not None
        assert p.CheckoutSession is not None
        assert p.IPaymentGateway is not None
