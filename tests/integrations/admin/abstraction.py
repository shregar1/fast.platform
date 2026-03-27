"""Module abstraction.py."""

from __future__ import annotations

from tests.integrations.abstraction import IIntegrationsSuite

"""Test-suite markers for ``admin`` (mirrors ``src/admin/``)."""


from abc import ABC


class IAdminTests(IIntegrationsSuite, ABC):
    """Marker base for test classes covering :mod:`admin`."""

    __slots__ = ()


__all__ = ["IAdminTests"]
