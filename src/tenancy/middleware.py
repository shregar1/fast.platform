"""
Tenant resolution and FastAPI middleware.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .context import Tenant, TenantStore, set_current_tenant


class TenantResolver(ABC):
    """Abstract base for resolving tenant from request."""

    @abstractmethod
    async def resolve(self, request: Request) -> Optional[Tenant]:
        """Resolve tenant from request. Return None if not found."""
        raise NotImplementedError


class HeaderTenantResolver(TenantResolver):
    """Resolve tenant from request header (e.g. X-Tenant-ID)."""

    def __init__(self, store: TenantStore, header_name: str = "X-Tenant-ID"):
        self._store = store
        self._header_name = header_name

    async def resolve(self, request: Request) -> Optional[Tenant]:
        tenant_id = request.headers.get(self._header_name)
        if tenant_id:
            return await self._store.get_by_id(tenant_id)
        return None


class SubdomainTenantResolver(TenantResolver):
    """Resolve tenant from subdomain (e.g. tenant1.example.com -> tenant1)."""

    def __init__(
        self,
        store: TenantStore,
        base_domain: str,
        excluded_subdomains: Optional[list[str]] = None,
    ):
        self._store = store
        self._base_domain = base_domain
        self._excluded = excluded_subdomains or ["www", "api", "admin"]

    async def resolve(self, request: Request) -> Optional[Tenant]:
        host = request.headers.get("host", "")
        if host.endswith(f".{self._base_domain}"):
            subdomain = host.replace(f".{self._base_domain}", "")
            if subdomain and subdomain not in self._excluded:
                return await self._store.get_by_slug(subdomain)
        return None


class PathTenantResolver(TenantResolver):
    """Resolve tenant from URL path (e.g. /t/tenant1/api/... -> tenant1)."""

    def __init__(self, store: TenantStore, prefix: str = "/t/"):
        self._store = store
        self._prefix = prefix

    async def resolve(self, request: Request) -> Optional[Tenant]:
        path = request.url.path
        if path.startswith(self._prefix):
            remaining = path[len(self._prefix) :].lstrip("/")
            parts = remaining.split("/", 1)
            if parts:
                return await self._store.get_by_slug(parts[0])
        return None


class JWTTenantResolver(TenantResolver):
    """Resolve tenant from JWT/user on request.state (e.g. request.state.user.tenant_id)."""

    def __init__(self, store: TenantStore, claim_name: str = "tenant_id"):
        self._store = store
        self._claim_name = claim_name

    async def resolve(self, request: Request) -> Optional[Tenant]:
        user = getattr(request.state, "user", None)
        if user is not None and hasattr(user, self._claim_name):
            tenant_id = getattr(user, self._claim_name)
            if tenant_id:
                return await self._store.get_by_id(tenant_id)
        return None


class ChainedTenantResolver(TenantResolver):
    """Try multiple resolvers in order until one returns a tenant."""

    def __init__(self, resolvers: list[TenantResolver]):
        self._resolvers = resolvers

    async def resolve(self, request: Request) -> Optional[Tenant]:
        for resolver in self._resolvers:
            tenant = await resolver.resolve(request)
            if tenant is not None:
                return tenant
        return None


class TenantMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that sets tenant context per request."""

    def __init__(
        self,
        app: Any,
        resolver: TenantResolver,
        required: bool = False,
        exclude_paths: Optional[set[str]] = None,
    ):
        super().__init__(app)
        self._resolver = resolver
        self._required = required
        self._exclude_paths = exclude_paths or {"/health", "/metrics", "/docs", "/openapi.json", "/redoc"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in self._exclude_paths:
            return await call_next(request)

        tenant = await self._resolver.resolve(request)

        if tenant is None and self._required:
            raise HTTPException(status_code=400, detail="Tenant not found or not specified")

        if tenant is not None and not tenant.is_active:
            raise HTTPException(status_code=403, detail="Tenant is not active")

        set_current_tenant(tenant)
        request.state.tenant = tenant
        request.state.tenant_id = tenant.id if tenant else None

        try:
            response = await call_next(request)
            if tenant is not None:
                response.headers["X-Tenant-ID"] = tenant.id
            return response
        finally:
            pass
