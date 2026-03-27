"""API Versioning for FastPlatform.

Simple URL-based API versioning.

Usage:
    from fastapi import FastAPI
    from fast_platform.core.utils.versioning import versioned_router, APIVersion

    app = FastAPI()

    # Create versioned router
    v1_router = versioned_router(version="v1", deprecated=False)

    @v1_router.get("/users")
    async def list_users_v1():
        return {"version": "v1", "users": []}

    # Another version
    v2_router = versioned_router(version="v2")

    @v2_router.get("/users")
    async def list_users_v2():
        return {"version": "v2", "users": [], "meta": {}}

    # Include in app
    app.include_router(v1_router, prefix="/api")
    app.include_router(v2_router, prefix="/api")

    # Results in:
    # GET /api/v1/users
    # GET /api/v2/users

Configuration:
    API_VERSION_DEFAULT=v1
    API_VERSION_DEPRECATED_HEADER=true
"""

from functools import wraps
from typing import Optional, Callable
from datetime import datetime

try:
    from fastapi import APIRouter, Request, Response
    from fastapi.responses import JSONResponse

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


class APIVersion:
    """Represents an API version."""

    def __init__(
        self,
        version: str,
        deprecated: bool = False,
        sunset_date: Optional[datetime] = None,
        docs_url: Optional[str] = None,
    ):
        """Execute __init__ operation.

        Args:
            version: The version parameter.
            deprecated: The deprecated parameter.
            sunset_date: The sunset_date parameter.
            docs_url: The docs_url parameter.
        """
        self.version = version
        self.deprecated = deprecated
        self.sunset_date = sunset_date
        self.docs_url = docs_url

    def __str__(self) -> str:
        """Execute __str__ operation.

        Returns:
            The result of the operation.
        """
        return self.version

    def to_header_dict(self) -> dict:
        """Convert to headers dict for responses."""
        headers = {"X-API-Version": self.version}

        if self.deprecated:
            headers["Deprecation"] = "true"
            if self.sunset_date:
                headers["Sunset"] = self.sunset_date.isoformat()

        return headers


def versioned_router(
    version: str,
    deprecated: bool = False,
    sunset_date: Optional[datetime] = None,
    default: bool = False,
    **router_kwargs,
):
    """Create an APIRouter with versioning support.

    Args:
        version: Version string (e.g., "v1", "v2", "2023-01")
        deprecated: Mark this version as deprecated
        sunset_date: When this version will be removed
        default: Whether this is the default version
        **router_kwargs: Additional arguments for APIRouter

    Returns:
        APIRouter with versioning configured

    """
    if not HAS_FASTAPI:
        raise ImportError("FastAPI is required for versioned_router")

    api_version = APIVersion(version, deprecated, sunset_date)

    # Create router
    router = APIRouter(prefix=f"/{version}", tags=[f"API {version}"], **router_kwargs)

    # Store version info on router
    router.api_version = api_version

    return router


def version(major: int, minor: int = 0) -> str:
    """Create a version string.

    Usage:
        version(1)      # "v1"
        version(1, 5)   # "v1.5"
    """
    if minor > 0:
        return f"v{major}.{minor}"
    return f"v{major}"


class VersionHeaderMiddleware:
    """Middleware that adds version headers to responses.

    Usage:
        from fastapi import FastAPI
        from fast_platform.core.utils.versioning import VersionHeaderMiddleware

        app = FastAPI()
        app.add_middleware(VersionHeaderMiddleware)
    """

    def __init__(self, app):
        """Execute __init__ operation.

        Args:
            app: The app parameter.
        """
        self.app = app

    async def __call__(self, scope, receive, send):
        """Execute __call__ operation.

        Args:
            scope: The scope parameter.
            receive: The receive parameter.
            send: The send parameter.

        Returns:
            The result of the operation.
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract version from path
        path = scope.get("path", "")
        version = self._extract_version(path)

        if version:
            # Wrap send to add headers
            async def send_with_headers(message):
                """Execute send_with_headers operation.

                Args:
                    message: The message parameter.

                Returns:
                    The result of the operation.
                """
                if message["type"] == "http.response.start":
                    headers = message.get("headers", [])

                    # Add version header
                    headers.append((b"x-api-version", version.encode()))

                    message["headers"] = headers

                await send(message)

            await self.app(scope, receive, send_with_headers)
        else:
            await self.app(scope, receive, send)

    def _extract_version(self, path: str) -> Optional[str]:
        """Extract version from URL path."""
        parts = path.strip("/").split("/")
        for part in parts:
            if part.startswith("v") and part[1:].replace(".", "").isdigit():
                return part
        return None


def deprecate(
    sunset_date: Optional[str] = None,
    alternative: Optional[str] = None,
    docs_url: Optional[str] = None,
):
    """Decorator to mark an endpoint as deprecated.

    Usage:
        @router.get("/old-endpoint")
        @deprecate(
            sunset_date="2024-06-01",
            alternative="/api/v2/new-endpoint"
        )
        async def old_endpoint():
            return {"message": "This is deprecated"}
    """

    def decorator(func: Callable) -> Callable:
        """Execute decorator operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            """Execute async_wrapper operation.

            Returns:
                The result of the operation.
            """
            response = await func(*args, **kwargs)

            # Add deprecation headers if response is dict
            if isinstance(response, dict):
                response["_meta"] = response.get("_meta", {})
                response["_meta"]["deprecated"] = True
                if sunset_date:
                    response["_meta"]["sunset_date"] = sunset_date
                if alternative:
                    response["_meta"]["alternative"] = alternative

            return response

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            """Execute sync_wrapper operation.

            Returns:
                The result of the operation.
            """
            response = func(*args, **kwargs)

            if isinstance(response, dict):
                response["_meta"] = response.get("_meta", {})
                response["_meta"]["deprecated"] = True
                if sunset_date:
                    response["_meta"]["sunset_date"] = sunset_date
                if alternative:
                    response["_meta"]["alternative"] = alternative

            return response

        # Check if function is async
        import inspect

        if inspect.iscoroutinefunction(func):
            wrapper = async_wrapper
        else:
            wrapper = sync_wrapper

        # Add deprecation info
        wrapper._deprecated = True
        wrapper._sunset_date = sunset_date
        wrapper._alternative = alternative

        return wrapper

    return decorator


class VersionManager:
    """Manages API versions and routing.

    Usage:
        manager = VersionManager()

        @manager.version("v1")
        def v1_routes():
            router = APIRouter()
            @router.get("/users")
            async def list_users():
                return []
            return router

        @manager.version("v2", deprecated=True)
        def v2_routes():
            router = APIRouter()
            @router.get("/users")
            async def list_users():
                return {"users": []}
            return router

        # Register with FastAPI
        app = FastAPI()
        manager.register_with_app(app, prefix="/api")
    """

    def __init__(self):
        """Execute __init__ operation."""
        self.versions: dict[str, dict] = {}

    def version(
        self, version: str, deprecated: bool = False, sunset_date: Optional[datetime] = None
    ):
        """Decorator to register routes for a version."""

        def decorator(func):
            """Execute decorator operation.

            Args:
                func: The func parameter.

            Returns:
                The result of the operation.
            """
            self.versions[version] = {
                "factory": func,
                "deprecated": deprecated,
                "sunset_date": sunset_date,
            }
            return func

        return decorator

    def register_with_app(self, app, prefix: str = "/api"):
        """Register all versions with FastAPI app."""
        if not HAS_FASTAPI:
            raise ImportError("FastAPI is required")

        for version_str, config in self.versions.items():
            router = config["factory"]()

            # Add deprecation info to routes
            if config["deprecated"]:
                for route in router.routes:
                    if hasattr(route, "responses"):
                        route.responses[200] = {
                            "headers": {
                                "Deprecation": {"type": "string"},
                                "Sunset": {"type": "string"},
                            }
                        }

            app.include_router(router, prefix=f"{prefix}/{version_str}")

    def get_versions(self) -> list[dict]:
        """Get list of available versions."""
        return [
            {
                "version": v,
                "deprecated": c["deprecated"],
                "sunset_date": c["sunset_date"].isoformat() if c["sunset_date"] else None,
            }
            for v, c in self.versions.items()
        ]


# Helper for creating version response
async def get_versions_endpoint(manager: VersionManager):
    """Endpoint that returns available API versions."""
    return {
        "versions": manager.get_versions(),
        "current": "v1",  # Default
        "latest": max(manager.versions.keys()) if manager.versions else "v1",
    }
