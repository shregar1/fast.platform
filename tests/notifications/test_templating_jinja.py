"""Jinja2 templating path."""

from __future__ import annotations

from unittest.mock import patch

import pytest


def test_render_jinja_string_ok() -> None:
    pytest.importorskip("jinja2")
    from fast_notifications.templating import render_jinja_string

    assert render_jinja_string("Hello {{ name }}", context={"name": "x"}) == "Hello x"


def test_render_jinja_import_error() -> None:
    import builtins

    import fast_notifications.templating as t

    real_import = builtins.__import__

    def guard(name: str, *a, **kw):
        if name == "jinja2":
            raise ImportError("no jinja")
        return real_import(name, *a, **kw)

    with patch.object(builtins, "__import__", side_effect=guard):
        with pytest.raises(RuntimeError, match="Jinja2"):
            t.render_jinja_string("x", context={})
