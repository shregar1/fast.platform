"""Tests for Jinja2 templating hook."""

import pytest

pytest.importorskip("jinja2")


def test_render_jinja_string():
    from fast_notifications.templating import render_jinja_string

    out = render_jinja_string("Hello {{ name }}", context={"name": "World"})
    assert out == "Hello World"
