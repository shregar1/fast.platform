"""
Logical categorization of top-level packages under ``fast_platform``'s ``src`` tree.

Physical layout stays flat (``configuration``, ``dtos``, …) under ``src/`` for import
stability. The **test suite** mirrors this taxonomy under ``tests/<section>/`` where
``section`` is :data:`SECTION_TEST_FOLDER` (e.g. ``tests/core/utils/``, ``tests/sec/security/``).
The ``SECURITY`` section uses folder name ``sec`` so package ``security`` can live at
``tests/sec/security/`` without path collision.

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
    # Data platform: search, vectors, object storage, cache
    DATA_PLATFORM = "data_platform"
    # Messaging & async: queues, Kafka, jobs, events, notifications, webhooks
    MESSAGING = "messaging"
    # Realtime: WebSocket-style channels, streams, WebRTC
    REALTIME = "realtime"
    # Product integrations: LLM, payments, media, analytics, admin
    INTEGRATIONS = "integrations"
    # Operations: observability, flags, tenancy, resilience, API versioning
    OPERATIONS = "operations"


# Every key must be exactly one importable top-level name under src/
PACKAGE_TO_SECTION: Final[dict[str, PackageSection]] = {
    # --- core ---
    "configuration": PackageSection.CORE,
    "dtos": PackageSection.CORE,
    "errors": PackageSection.CORE,
    "utils": PackageSection.CORE,
    "services": PackageSection.CORE,
    "fast_platform": PackageSection.CORE,
    # --- security ---
    "security": PackageSection.SECURITY,
    "secrets": PackageSection.SECURITY,
    "identity": PackageSection.SECURITY,
    # --- persistence ---
    "db": PackageSection.PERSISTENCE,
    "datastores": PackageSection.PERSISTENCE,
    # --- data platform ---
    "search": PackageSection.DATA_PLATFORM,
    "vectors": PackageSection.DATA_PLATFORM,
    "storage": PackageSection.DATA_PLATFORM,
    "cache": PackageSection.DATA_PLATFORM,
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
    PackageSection.DATA_PLATFORM: "data_platform",
    PackageSection.MESSAGING: "messaging",
    PackageSection.REALTIME: "realtime",
    PackageSection.INTEGRATIONS: "integrations",
    PackageSection.OPERATIONS: "operations",
}


def _build_section_to_packages() -> dict[PackageSection, frozenset[str]]:
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
    """
    Top-level directory names under ``src`` that look like Python packages
    (directory containing ``__init__.py`` or a plain namespace layout).

    Used by tests to ensure the taxonomy stays in sync with the tree.
    """

    root = src_root or Path(__file__).resolve().parents[1]
    names: set[str] = set()
    if not root.is_dir():
        return frozenset()
    for p in root.iterdir():
        if not p.is_dir() or p.name.startswith(("_", ".")):
            continue
        if (p / "__init__.py").is_file():
            names.add(p.name)
    return frozenset(names)
