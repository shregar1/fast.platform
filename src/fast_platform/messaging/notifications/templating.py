"""Optional Jinja2 rendering for notification bodies (install ``fast_notifications[jinja2]``)."""

from __future__ import annotations

from typing import Any


def render_jinja_string(template: str, *, context: dict[str, Any]) -> str:
    """Render a template string with ``context`` (autoescaping enabled).

    Raises:
        RuntimeError: if Jinja2 is not installed.
        jinja2.TemplateError: on invalid template syntax.

    """
    try:
        from jinja2 import Environment
    except ImportError as exc:
        raise RuntimeError(
            "Jinja2 is not installed. Use: pip install 'fast_notifications[jinja2]'"
        ) from exc
    env = Environment(autoescape=True)
    return env.from_string(template).render(**context)
