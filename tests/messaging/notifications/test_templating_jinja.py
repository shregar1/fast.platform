"""Module test_templating_jinja.py."""

from __future__ import annotations

"""Jinja2 templating path."""
from unittest.mock import patch

import pytest

from tests.messaging.notifications.abstraction import INotificationTests


class TestTemplatingJinja(INotificationTests):
    """Represents the TestTemplatingJinja class."""

    def test_render_jinja_string_ok(self) -> None:
        """Execute test_render_jinja_string_ok operation.

        Returns:
            The result of the operation.
        """
        pytest.importorskip("jinja2")
        from fast_platform.messaging.notifications.templating import render_jinja_string

        assert render_jinja_string("Hello {{ name }}", context={"name": "x"}) == "Hello x"

    def test_render_jinja_import_error(self) -> None:
        """Execute test_render_jinja_import_error operation.

        Returns:
            The result of the operation.
        """
        import builtins

        import fast_platform.messaging.notifications.templating as t

        real_import = builtins.__import__

        def guard(name: str, *a, **kw):
            """Execute guard operation.

            Args:
                name: The name parameter.

            Returns:
                The result of the operation.
            """
            if name == "jinja2":
                raise ImportError("no jinja")
            return real_import(name, *a, **kw)

        with patch.object(builtins, "__import__", side_effect=guard):
            with pytest.raises(RuntimeError, match="Jinja2"):
                t.render_jinja_string("x", context={})
