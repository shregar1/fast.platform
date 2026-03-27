"""Module abstraction.py."""

from __future__ import annotations

"""Test-suite markers for ``identity`` (mirrors ``src/identity/``)."""

from abc import ABC

from tests.sec.abstraction import ISecuritySuite


class IIdentityTests(ISecuritySuite, ABC):
    """Marker base for test classes covering :mod:`identity`."""

    __slots__ = ()


__all__ = ["IIdentityTests"]
