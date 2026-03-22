"""
Optional dependency loading without failing the whole application at import time.

Use this pattern for **extras** (PDF, Pillow, vector DBs) so core code paths
import cleanly in minimal environments while optional features resolve their
implementations at runtime. Any import or attribute error is treated as “missing”
and returns ``(None, None)`` or ``(module, None)`` as documented below.
"""

from __future__ import annotations

import importlib
from typing import Any, Tuple

__all__ = ["OptionalImports"]


class OptionalImports:
    """
    Resolve optional third-party modules and attributes defensively.

    Typical usage in utility classes::

        mod, PdfReader = OptionalImports.optional_import("pypdf", "PdfReader")
        if PdfReader is None:
            return None
        reader = PdfReader(...)
    """

    @staticmethod
    def optional_import(module: str, attr: str | None = None) -> Tuple[Any | None, Any | None]:
        """
        Import *module* and optionally retrieve *attr* from it.

        If ``importlib.import_module(module)`` raises any exception, returns
        ``(None, None)``. If *attr* is ``None``, returns ``(module, None)`` on
        success. If *attr* is set, returns ``(module, getattr(module, attr))``
        on success; if ``getattr`` raises, returns ``(module, None)`` so callers
        can distinguish “module present, attribute missing” from total failure.

        Parameters
        ----------
        module:
            Dotted name, e.g. ``"pypdf"`` or ``"PIL.Image"``.
        attr:
            If given, name of an attribute to fetch from the imported module
            (often a class or function).

        Returns
        -------
        tuple
            ``(imported_module_or_None, attribute_or_None)``.
        """
        try:
            mod = importlib.import_module(module)
        except Exception:
            return None, None
        if attr is None:
            return mod, None
        try:
            return mod, getattr(mod, attr)
        except Exception:
            return mod, None
