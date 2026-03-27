"""PDF metadata and text extraction via optional ``pypdf``.

Install with ``pip install pypdf`` or the ``fast-platform[utils-pdf]`` extra.
When ``pypdf`` is not installed, public methods return ``None`` (they do not
raise). When parsing fails (corrupt bytes, truncated file), methods also return
``None``—callers that need diagnostics should validate inputs or use ``pypdf``
directly.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any, Optional, Type, Union

from ..optional_imports import OptionalImports

from .abstraction import IMedia

__all__ = ["PdfUtility"]


class PdfUtility(IMedia):
    """Read-only PDF helpers built on ``pypdf`` (optional dependency).

    Use for page counts and best-effort text extraction in pipelines or
    ingestion jobs. **Text extraction** quality depends on how the PDF encodes
    text (vector fonts, scans, etc.); this is not OCR. For scanned documents,
    integrate a dedicated OCR stack.

    **Dependencies:** ``pypdf`` must be importable. If not, all methods return
    ``None`` as documented per method.
    """

    @staticmethod
    def _reader_cls() -> Optional[Type[Any]]:
        """Resolve ``pypdf.PdfReader`` or return ``None`` if the package is missing.

        Returns
        -------
        type or None
            The ``PdfReader`` class, or ``None`` if ``pypdf`` cannot be loaded.

        """
        mod, PdfReader = OptionalImports.optional_import("pypdf", "PdfReader")
        if mod is None or PdfReader is None:
            return None
        return PdfReader

    @staticmethod
    def page_count(data: bytes) -> int | None:
        """Return the number of pages in a PDF given as in-memory bytes.

        Parameters
        ----------
        data:
            Complete PDF file contents (not a prefix).

        Returns
        -------
        int or None
            Page count, or ``None`` if ``pypdf`` is unavailable or parsing fails.

        """
        PdfReader = PdfUtility._reader_cls()
        if PdfReader is None:
            return None

        try:
            reader = PdfReader(BytesIO(data))
            return len(reader.pages)
        except Exception:
            return None

    @staticmethod
    def page_count_path(path: Union[str, Path]) -> int | None:
        """Return the number of pages in a PDF file on disk.

        Parameters
        ----------
        path:
            Filesystem path readable by the current process.

        Returns
        -------
        int or None
            Page count, or ``None`` if ``pypdf`` is unavailable or parsing fails.

        """
        PdfReader = PdfUtility._reader_cls()
        if PdfReader is None:
            return None
        try:
            reader = PdfReader(Path(path))
            return len(reader.pages)
        except Exception:
            return None

    @staticmethod
    def extract_text(data: bytes, *, max_pages: int | None = None) -> str | None:
        r"""Extract and concatenate textual content from PDF pages (best-effort).

        Iterates pages in order (``page.extract_text()`` per page). ``max_pages``
        limits how many pages are read from the start—useful to cap CPU on very
        large documents. Empty pages contribute nothing; the result is ``"\\n"``
        joined non-empty strings.

        Parameters
        ----------
        data:
            Complete PDF file contents.
        max_pages:
            If set, at most this many pages from the beginning are processed.
            If ``None``, all pages are processed.

        Returns
        -------
        str or None
            Extracted text, or ``None`` if ``pypdf`` is missing or the whole
            document fails to parse.

        """
        PdfReader = PdfUtility._reader_cls()
        if PdfReader is None:
            return None

        try:
            reader = PdfReader(BytesIO(data))
            parts: list[str] = []
            n = len(reader.pages)
            limit = n if max_pages is None else min(n, max_pages)
            for i in range(limit):
                page = reader.pages[i]
                t = page.extract_text()
                if t:
                    parts.append(t)
            return "\n".join(parts)
        except Exception:
            return None
