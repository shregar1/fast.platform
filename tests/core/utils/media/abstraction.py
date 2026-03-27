"""Module abstraction.py."""

from __future__ import annotations

"""Test-suite markers for ``utils/media`` (mirrors ``src/utils/media/``)."""

from abc import ABC

from tests.core.utils.abstraction import IUtilsTests


class IMediaUtilsTests(IUtilsTests, ABC):
    """Marker base for test classes covering :mod:`utils.media`."""

    __slots__ = ()


__all__ = ["IMediaUtilsTests"]
