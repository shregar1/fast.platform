from __future__ import annotations

"""Tests for :mod:`utils.media.text`."""
from tests.core.utils.media.abstraction import IMediaUtilsTests
from utils.media.text import TextUtility


class TestTextUtility(IMediaUtilsTests):
    def test_slugify(self) -> None:
        assert TextUtility.slugify("Café Menu!") == "cafe-menu"

    def test_collapse_whitespace(self) -> None:
        assert TextUtility.collapse_whitespace("  a \n b  ") == "a b"

    def test_truncate(self) -> None:
        assert TextUtility.truncate("abcdef", max_chars=4) == "abc…"
