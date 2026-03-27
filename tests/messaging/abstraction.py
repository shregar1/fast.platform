"""Module abstraction.py."""

from __future__ import annotations

"""Section suite for ``PackageSection.MESSAGING``."""

from abc import ABC

from tests.abstraction import ITest


class IMessagingSuite(ITest, ABC):
    """Marker for test classes under taxonomy section ``messaging``."""

    __slots__ = ()


__all__ = ["IMessagingSuite"]
