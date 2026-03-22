from __future__ import annotations

"""Test-suite markers for ``secrets`` (mirrors ``src/secrets/``)."""

from abc import ABC

from tests.sec.abstraction import ISecuritySuite


class ISecretsTests(ISecuritySuite, ABC):
    """Marker base for test classes covering :mod:`secrets`."""

    __slots__ = ()


__all__ = ["ISecretsTests"]
