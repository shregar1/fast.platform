"""Plain-text helpers: URL slugs, whitespace normalization, and truncation.

These are display- and routing-oriented string transforms. They do not implement
full Unicode identifier rules or database collation; adjust for your locale and
product requirements if slugs must be unique or stable across Unicode versions.
"""

from __future__ import annotations

import re
import unicodedata

from .abstraction import IMedia

__all__ = ["TextUtility"]


class TextUtility(IMedia):
    """String shaping for URLs, UI previews, and log lines.

    All methods are pure (no I/O) and operate on Unicode strings. :meth:`slugify`
    normalizes to ASCII-ish tokens; :meth:`collapse_whitespace` is useful before
    embeddings or search; :meth:`truncate` preserves a visible prefix with an
    ellipsis-style suffix.
    """

    _NON_ALNUM = re.compile(r"[^a-z0-9]+")

    @staticmethod
    def slugify(value: str, *, max_length: int | None = 64) -> str:
        """Produce a URL-friendly ASCII slug from arbitrary Unicode *value*.

        Steps: NFKD normalization, drop non-ASCII bytes, lowercase, replace runs
        of non-alphanumeric characters with a single hyphen, strip leading and
        trailing hyphens, then optionally truncate to ``max_length`` (without
        leaving a trailing hyphen after cut). If the result is empty, returns
        ``"n-a"``.

        Parameters
        ----------
        value:
            Arbitrary text (titles, filenames, etc.).
        max_length:
            Maximum length of the returned slug, or ``None`` for no limit.

        Returns
        -------
        str
            A hyphen-separated slug safe for typical URL path segments.

        Example
        -------
        ``"Café Menu!"`` → ``"cafe-menu"``.

        """
        s = unicodedata.normalize("NFKD", value)
        s = s.encode("ascii", "ignore").decode("ascii")
        s = s.lower().strip()
        s = TextUtility._NON_ALNUM.sub("-", s)
        s = s.strip("-")
        if max_length is not None and len(s) > max_length:
            s = s[:max_length].rstrip("-")
        return s or "n-a"

    @staticmethod
    def collapse_whitespace(text: str) -> str:
        """Replace all runs of Unicode whitespace with a single ASCII space.

        Leading and trailing whitespace are removed. Equivalent in effect to
        ``" ".join(text.split())``.

        Parameters
        ----------
        text:
            Arbitrary string.

        Returns
        -------
        str
            Single-space–separated tokens with no outer whitespace.

        """
        return " ".join(text.split())

    @staticmethod
    def truncate(text: str, *, max_chars: int, suffix: str = "…") -> str:
        """Shorten *text* to at most *max_chars* characters, appending *suffix* when truncated.

        The suffix counts toward *max_chars* when shortening: the visible prefix
        is ``text[0 : max_chars - len(suffix)]`` plus *suffix*. If *max_chars*
        is non-positive, returns ``""``. If *suffix* alone is longer than
        *max_chars*, returns *suffix* sliced to *max_chars*.

        Parameters
        ----------
        text:
            Full string to possibly shorten.
        max_chars:
            Maximum total length of the result (including suffix when used).
        suffix:
            Appended when *text* is longer than *max_chars* (default Unicode ellipsis).

        Returns
        -------
        str
            Original *text* if short enough, otherwise a truncated string with *suffix*.

        """
        if max_chars <= 0:
            return ""
        if len(text) <= max_chars:
            return text
        if len(suffix) >= max_chars:
            return suffix[:max_chars]
        return text[: max_chars - len(suffix)] + suffix
