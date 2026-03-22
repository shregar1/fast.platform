from __future__ import annotations
from tests.messaging.abstraction import IMessagingSuite
"""Test-suite markers for ``webhooks`` (mirrors ``src/webhooks/``)."""


from abc import ABC



class IWebhookTests(IMessagingSuite, ABC):
    """Marker base for test classes covering :mod:`webhooks`."""

    __slots__ = ()


__all__ = ["IWebhookTests"]
