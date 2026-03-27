"""Module abstraction.py."""

from __future__ import annotations

from tests.integrations.abstraction import IIntegrationsSuite

"""Test-suite markers for ``payments`` (mirrors ``src/payments/``)."""


from abc import ABC


class IPaymentsTests(IIntegrationsSuite, ABC):
    """Marker base for test classes covering :mod:`payments`."""

    __slots__ = ()


__all__ = ["IPaymentsTests"]
