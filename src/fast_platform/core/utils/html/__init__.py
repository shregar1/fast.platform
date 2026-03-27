"""HTML utilities (escaping, tag stripping)."""

from .abstraction import IHtmlUtility
from .html import HtmlUtility

__all__ = ["HtmlUtility", "IHtmlUtility"]
