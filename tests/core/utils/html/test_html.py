"""Module test_html.py."""

from __future__ import annotations

"""Tests for :mod:`utils.html`."""
from tests.core.utils.html.abstraction import IHtmlUtilsTests
from core.utils.html import HtmlUtility


class TestHtmlUtility(IHtmlUtilsTests):
    """Represents the TestHtmlUtility class."""

    def test_escape(self) -> None:
        """Execute test_escape operation.

        Returns:
            The result of the operation.
        """
        assert "&" in HtmlUtility.escape("<a>&\"'")
        assert "<" not in HtmlUtility.escape("<")

    def test_strip_tags(self) -> None:
        """Execute test_strip_tags operation.

        Returns:
            The result of the operation.
        """
        assert HtmlUtility.strip_tags("<p>Hi &amp; <b>there</b></p>") == "Hi & there"

    def test_strip_tags_regex(self) -> None:
        """Execute test_strip_tags_regex operation.

        Returns:
            The result of the operation.
        """
        assert HtmlUtility.strip_tags_regex("<div>x</div>") == "x"
