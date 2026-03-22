"""Smoke test package import."""

def test_import():
    import fast_payments as p
    assert p.PaymentsConfiguration is not None
    assert p.PaymentsConfigurationDTO is not None
    assert p.CheckoutSession is not None
    assert p.IPaymentGateway is not None
