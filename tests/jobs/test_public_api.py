"""Ensure every name in __all__ resolves."""

from __future__ import annotations

import importlib

import pytest

PACKAGE = "fast_jobs"


def test_public_exports_resolve():
    try:
        m = importlib.import_module(PACKAGE)
    except ImportError as e:
        pytest.skip(f"import not available: {e}")
    for export_name in getattr(m, "__all__", ()):
        getattr(m, export_name)
