"""Tests for Jinja2 templating hook."""

import pytest

from tests.messaging.notifications.abstraction import INotificationTests

pytest.importorskip("jinja2")


class TestTemplating(INotificationTests):
    def test_render_jinja_string(self):
        from messaging.notifications.templating import render_jinja_string

        out = render_jinja_string("Hello {{ name }}", context={"name": "World"})
        assert out == "Hello World"
