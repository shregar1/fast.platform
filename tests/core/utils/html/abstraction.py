from __future__ import annotations

"""Test-suite markers for ``utils/html`` (mirrors ``src/utils/html/``)."""

from abc import ABC

from tests.core.utils.abstraction import IUtilsTests


class IHtmlUtilsTests(IUtilsTests, ABC):
    """Marker base for test classes covering :mod:`utils.html`."""

    __slots__ = ()


__all__ = ["IHtmlUtilsTests"]
