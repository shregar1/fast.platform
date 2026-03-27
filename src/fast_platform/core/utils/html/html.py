"""HTML escaping and lightweight tag stripping using the standard library.

These helpers are suitable for **escaping** dynamic text before embedding it in
HTML or attributes, and for **rough** conversion of HTML-ish strings to plain
text (logs, previews, notifications). They are **not** a substitute for a
policy-based HTML sanitizer (e.g. bleach) when rendering untrusted rich HTML in
a browser: stripping tags does not remove dangerous URLs, ``<script>`` in
attributes, or CSS-based attacks.
"""

from __future__ import annotations

import html
import re

from .abstraction import IHtmlUtility

from .html_strip_tags_parser import HtmlStripTagsParser

__all__ = ["HtmlUtility"]


class HtmlUtility(IHtmlUtility):
    """HTML escaping and plain-text extraction helpers.

    **Escaping:** use :meth:`escape` / :meth:`escape_attribute` whenever user or
    external data is interpolated into HTML documents or quoted attributes.

    **Stripping:** :meth:`strip_tags` uses the stdlib parser and resolves
    entities; :meth:`strip_tags_regex` is faster but naive and can mis-handle
    malformed markup or ``<`` in text. For untrusted rich HTML in the DOM, use a
    dedicated sanitizer library instead of tag stripping alone.
    """

    _TAG_RE = re.compile(r"<[^>]+>")

    @staticmethod
    def escape(text: str) -> str:
        """Escape characters that are special in HTML text and in double-quoted attributes.

        Escapes ``&``, ``<``, ``>``, ``"``, and ``'`` so the result is safe to
        embed in HTML body text or inside ``"..."`` attributes when ``quote=True``
        (same as :func:`html.escape` with ``quote=True``).

        Parameters
        ----------
        text:
            Raw string that may contain HTML-significant characters.

        Returns
        -------
        str
            Escaped string safe for HTML contexts described above.

        """
        return html.escape(text, quote=True)

    @staticmethod
    def escape_attribute(text: str) -> str:
        """Escape a value intended for a double-quoted HTML attribute.

        Currently equivalent to :meth:`escape` (both use ``quote=True``). Kept
        as a named entry point so call sites document intent (attribute context).

        Parameters
        ----------
        text:
            Raw attribute value.

        Returns
        -------
        str
            Escaped string suitable for ``attr="..."``.

        """
        return html.escape(text, quote=True)

    @staticmethod
    def strip_tags(html_fragment: str) -> str:
        """Remove HTML tags and return visible text with normalized whitespace.

        Uses :class:`~utils.html_strip_tags_parser.HtmlStripTagsParser` so character references are decoded to
        Unicode. After parsing, internal runs of whitespace are collapsed to a
        single space (split/join), which is usually desirable for previews but
        may differ from browser text extraction for ``<pre>``-style content.

        Parameters
        ----------
        html_fragment:
            A snippet or full document; does not need to be balanced or valid HTML.

        Returns
        -------
        str
            Plain text with tags removed and whitespace collapsed.

        """
        parser = HtmlStripTagsParser()
        parser.feed(html_fragment)
        parser.close()
        return " ".join(parser.get_text().split())

    @staticmethod
    def strip_tags_regex(html_fragment: str) -> str:
        """Remove substrings that look like ``<...>`` using a regular expression.

        Faster than :meth:`strip_tags` but **not** an HTML parser: edge cases
        such as ``<`` in text, comments, or malformed tags may produce surprising
        results. Whitespace is normalized the same way as :meth:`strip_tags`.

        Parameters
        ----------
        html_fragment:
            Source string to strip.

        Returns
        -------
        str
            Text with regex-matched tag-like segments replaced by spaces, then collapsed.

        """
        text = HtmlUtility._TAG_RE.sub(" ", html_fragment)
        return " ".join(text.split())
