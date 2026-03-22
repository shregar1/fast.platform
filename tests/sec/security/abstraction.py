from __future__ import annotations

"""Test-suite markers for ``security`` (mirrors ``src/security/``)."""

from abc import ABC

from tests.sec.abstraction import ISecuritySuite


class ISecurityTests(ISecuritySuite, ABC):
    """Marker base for test classes covering :mod:`security`."""

    __slots__ = ()


__all__ = ["ISecurityTests"]
