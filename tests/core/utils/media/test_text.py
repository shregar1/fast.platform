"""Module test_text.py."""

from __future__ import annotations

"""Tests for :mod:`utils.media.text`."""
from tests.core.utils.media.abstraction import IMediaUtilsTests
from fast_platform.core.utils.media.text import TextUtility


class TestTextUtility(IMediaUtilsTests):
    """Represents the TestTextUtility class."""

    def test_slugify(self) -> None:
        """Execute test_slugify operation.

        Returns:
            The result of the operation.
        """
        assert TextUtility.slugify("Café Menu!") == "cafe-menu"

    def test_collapse_whitespace(self) -> None:
        """Execute test_collapse_whitespace operation.

        Returns:
            The result of the operation.
        """
        assert TextUtility.collapse_whitespace("  a \n b  ") == "a b"

    def test_truncate(self) -> None:
        """Execute test_truncate operation.

        Returns:
            The result of the operation.
        """
        assert TextUtility.truncate("abcdef", max_chars=4) == "abc…"
