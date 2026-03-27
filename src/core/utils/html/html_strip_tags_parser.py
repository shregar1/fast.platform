"""HTML parser that collects visible text from a fragment (tags ignored).

Used by :class:`~utils.html.HtmlUtility` for :meth:`~utils.html.HtmlUtility.strip_tags`.
"""

from __future__ import annotations

from html.parser import HTMLParser
from io import StringIO

__all__ = ["HtmlStripTagsParser"]


class HtmlStripTagsParser(HTMLParser):
    """Collect visible character data from an HTML fragment, ignoring tags.

    Subclasses :class:`html.parser.HTMLParser` with ``convert_charrefs=True`` so
    numeric and named character references in the source become Unicode text in
    the collected output. Tags are not echoed into the buffer—only
    :meth:`~html.parser.HTMLParser.handle_data` runs for text nodes.
    """

    def __init__(self) -> None:
        """Execute __init__ operation."""
        super().__init__(convert_charrefs=True)
        self._buf = StringIO()

    def handle_data(self, data: str) -> None:
        """Append literal text content (not tags) to the internal buffer."""
        self._buf.write(data)

    def get_text(self) -> str:
        """Return all text collected from :meth:`handle_data` without further processing."""
        return self._buf.getvalue()
