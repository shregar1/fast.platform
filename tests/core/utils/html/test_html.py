from __future__ import annotations

"""Tests for :mod:`utils.html`."""
from tests.core.utils.html.abstraction import IHtmlUtilsTests
from core.utils.html import HtmlUtility


class TestHtmlUtility(IHtmlUtilsTests):
    def test_escape(self) -> None:
        assert "&" in HtmlUtility.escape("<a>&\"'")
        assert "<" not in HtmlUtility.escape("<")

    def test_strip_tags(self) -> None:
        assert HtmlUtility.strip_tags("<p>Hi &amp; <b>there</b></p>") == "Hi & there"

    def test_strip_tags_regex(self) -> None:
        assert HtmlUtility.strip_tags_regex("<div>x</div>") == "x"
