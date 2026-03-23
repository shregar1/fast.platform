"""API versioning for FastAPI (URL path, header, query). Prefer ``from fast_versioning import …``; ``core.versioning`` in pyfastmvc re-exports the same API."""

from fast_versioning.router import (
    APIVersion,
    VersionedAPIRouter,
    VersioningMiddleware,
    VersioningStrategy,
    get_api_version,
    versioned_router,
)

__all__ = [
    "APIVersion",
    "VersionedAPIRouter",
    "VersioningMiddleware",
    "VersioningStrategy",
    "versioned_router",
    "get_api_version",
]
