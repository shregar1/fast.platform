"""Logical categorization of domain packages under ``fast_platform``'s ``src`` tree.

Physical layout nests each domain package under a **section folder** (e.g.
``src/core/configuration``, ``src/sec/security``) matching :class:`PackageSection`.
The meta-package :mod:`fast_platform` stays at ``src/fast_platform`` (public entry point).

The **test suite** mirrors the same taxonomy under ``tests/<section>/`` where
``section`` is :data:`SECTION_TEST_FOLDER` (e.g. ``tests/core/utils/``,
``tests/sec/security/``). The ``SECURITY`` section uses folder name ``sec`` so package
``security`` can live at ``tests/sec/security/`` without path collision.
are
This module is the **canonical map** for docs, CI splits, and navigation.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Final

__all__ = [
    "PackageSection",
    "PACKAGE_TO_SECTION",
    "SECTION_TEST_FOLDER",
    "SECTION_TO_PACKAGES",
    "packages_in_section",
    "section_of",
    "all_taxonomy_packages",
    "discover_src_packages",
]


class PackageSection(str, Enum):
    """Deep category for each installable top-level package."""

    # Core: config, schemas, errors, helpers, orchestration services
    CORE = "core"
    # Security: crypto, API keys, identity, secret backends
    SECURITY = "security"
    # Persistence: SQLAlchemy + multi-backend datastores
    PERSISTENCE = "persistence"
    # Data: search, vectors, object storage, cache
    DATA = "data"
    # Messaging & async: queues, Kafka, jobs, events, notifications, webhooks
    MESSAGING = "messaging"
    # Realtime: WebSocket-style channels, streams, WebRTC
    REALTIME = "realtime"
    # Product integrations: LLM, payments, media, analytics, admin
    INTEGRATIONS = "integrations"
    # Operations: observability, flags, tenancy, resilience, API versioning
    OPERATIONS = "operations"


# Every key is the *leaf* import name (e.g. ``configuration`` → ``core.configuration``).
PACKAGE_TO_SECTION: Final[dict[str, PackageSection]] = {
    # --- core ---
    "configuration": PackageSection.CORE,
    "dtos": PackageSection.CORE,
    "errors": PackageSection.CORE,
    "utils": PackageSection.CORE,
    "service": PackageSection.CORE,
    "fast_platform": PackageSection.CORE,
    # --- security ---
    "security": PackageSection.SECURITY,
    "secrets": PackageSection.SECURITY,
    "identity": PackageSection.SECURITY,
    # --- persistence ---
    "db": PackageSection.PERSISTENCE,
    "datastores": PackageSection.PERSISTENCE,
    # --- data platform ---
    "search": PackageSection.DATA,
    "vectors": PackageSection.DATA,
    "storage": PackageSection.DATA,
    "cache": PackageSection.DATA,
    # --- messaging ---
    "kafka": PackageSection.MESSAGING,
    "queues": PackageSection.MESSAGING,
    "events": PackageSection.MESSAGING,
    "jobs": PackageSection.MESSAGING,
    "notifications": PackageSection.MESSAGING,
    "webhooks": PackageSection.MESSAGING,
    # --- realtime ---
    "channels": PackageSection.REALTIME,
    "streams": PackageSection.REALTIME,
    "webrtc": PackageSection.REALTIME,
    # --- integrations ---
    "llm": PackageSection.INTEGRATIONS,
    "payments": PackageSection.INTEGRATIONS,
    "media": PackageSection.INTEGRATIONS,
    "analytics": PackageSection.INTEGRATIONS,
    "admin": PackageSection.INTEGRATIONS,
    # --- operations ---
    "observability": PackageSection.OPERATIONS,
    "otel": PackageSection.OPERATIONS,
    "resilience": PackageSection.OPERATIONS,
    "tenancy": PackageSection.OPERATIONS,
    "versioning": PackageSection.OPERATIONS,
    "features": PackageSection.OPERATIONS,
}

# Directory name under ``tests/<section>/`` for each :class:`PackageSection`.
# ``SECURITY`` uses ``sec`` so package ``security`` can live at ``tests/sec/security/``
# without colliding with the section folder name.
SECTION_TEST_FOLDER: Final[dict[PackageSection, str]] = {
    PackageSection.CORE: "core",
    PackageSection.SECURITY: "sec",
    PackageSection.PERSISTENCE: "persistence",
    PackageSection.DATA: "data",
    PackageSection.MESSAGING: "messaging",
    PackageSection.REALTIME: "realtime",
    PackageSection.INTEGRATIONS: "integrations",
    PackageSection.OPERATIONS: "operations",
}


def _build_section_to_packages() -> dict[PackageSection, frozenset[str]]:
    """Execute _build_section_to_packages operation.

    Returns:
        The result of the operation.
    """
    out: dict[PackageSection, set[str]] = {s: set() for s in PackageSection}
    for pkg, sec in PACKAGE_TO_SECTION.items():
        out[sec].add(pkg)
    return {s: frozenset(names) for s, names in out.items()}


SECTION_TO_PACKAGES: Final[dict[PackageSection, frozenset[str]]] = _build_section_to_packages()


def packages_in_section(section: PackageSection) -> frozenset[str]:
    """Return all top-level package names in *section*."""
    return SECTION_TO_PACKAGES[section]


def section_of(package: str) -> PackageSection:
    """Return the section for *package* (must exist in :data:`PACKAGE_TO_SECTION`)."""
    return PACKAGE_TO_SECTION[package]


def all_taxonomy_packages() -> frozenset[str]:
    """All packages registered in the taxonomy."""
    return frozenset(PACKAGE_TO_SECTION.keys())


def discover_src_packages(src_root: Path | None = None) -> frozenset[str]:
    """Leaf package names under ``src`` (e.g. ``configuration``, ``kafka``): each is a
    directory containing ``__init__.py``, nested under its taxonomy section folder
    (see :data:`SECTION_TEST_FOLDER`). The :mod:`fast_platform` meta-package is a
    direct child of ``src`` and is included when present.

    Used by tests to ensure the taxonomy stays in sync with the tree.
    """
    root = src_root or Path(__file__).resolve().parents[1]
    names: set[str] = set()
    if not root.is_dir():
        return frozenset()
    if (root / "fast_platform" / "__init__.py").is_file():
        names.add("fast_platform")
    section_dirs = frozenset(SECTION_TEST_FOLDER.values())
    for p in root.iterdir():
        if not p.is_dir() or p.name.startswith(("_", ".")):
            continue
        if p.name == "fast_platform":
            continue
        if p.name not in section_dirs:
            continue
        if not (p / "__init__.py").is_file():
            continue
        for q in p.iterdir():
            if not q.is_dir() or q.name.startswith(("_", ".")):
                continue
            if (q / "__init__.py").is_file():
                names.add(q.name)
    return frozenset(names)
