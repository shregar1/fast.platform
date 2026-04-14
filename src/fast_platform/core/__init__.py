"""Taxonomy section package (see :mod:`fast_platform.taxonomy`).

Application utilities (auth, audit, tracing, encryption, database helpers, webhooks,
registry, metrics, health, etc.) live in sibling modules under this package, for example
:mod:`fast_platform.core.auth` and :mod:`fast_platform.core.tracing`. The
``fast_dashboards.core`` namespace re-exports them for backward compatibility; new code
should import from ``fast_platform.core`` (or the specific submodule).
"""

from .abstraction import ICore

__all__ = ["ICore"]
