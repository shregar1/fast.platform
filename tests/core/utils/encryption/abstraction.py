"""Module abstraction.py."""

from __future__ import annotations

"""Test-suite markers for ``utils/encryption`` (mirrors ``src/utils/encryption/``)."""

from abc import ABC

from tests.core.utils.abstraction import IUtilsTests


class IEncryptionUtilsTests(IUtilsTests, ABC):
    """Marker base for test classes covering :mod:`utils.encryption`."""

    __slots__ = ()


__all__ = ["IEncryptionUtilsTests"]
