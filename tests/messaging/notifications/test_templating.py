"""Tests for Jinja2 templating hook."""

import pytest

from tests.messaging.notifications.abstraction import INotificationTests

pytest.importorskip("jinja2")


class TestTemplating(INotificationTests):
    """Represents the TestTemplating class."""

    def test_render_jinja_string(self):
        """Execute test_render_jinja_string operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.messaging.notifications.templating import render_jinja_string

        out = render_jinja_string("Hello {{ name }}", context={"name": "World"})
        assert out == "Hello World"
