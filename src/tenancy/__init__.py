"""
fast_tenancy – Multi-tenancy (tenant context, JWT, middleware) for FastMVC.
"""

from .context import (
    Tenant,
    TenantConfig,
    TenantContext,
    TenantStore,
    InMemoryTenantStore,
    get_current_tenant,
    get_current_tenant_id,
    set_current_tenant,
    clear_current_tenant,
)
from .middleware import (
    TenantResolver,
    HeaderTenantResolver,
    SubdomainTenantResolver,
    PathTenantResolver,
    JWTTenantResolver,
    ChainedTenantResolver,
    TenantMiddleware,
)
from .resolution import (
    ResolutionStrategy,
    ResolverSpec,
    TenantResolverRegistry,
    default_registry,
    subdomain_then_header,
)

__version__ = "0.1.1"

__all__ = [
    "Tenant",
    "TenantConfig",
    "TenantContext",
    "TenantStore",
    "InMemoryTenantStore",
    "get_current_tenant",
    "get_current_tenant_id",
    "set_current_tenant",
    "clear_current_tenant",
    "TenantResolver",
    "HeaderTenantResolver",
    "SubdomainTenantResolver",
    "PathTenantResolver",
    "JWTTenantResolver",
    "ChainedTenantResolver",
    "TenantMiddleware",
    "ResolutionStrategy",
    "ResolverSpec",
    "TenantResolverRegistry",
    "default_registry",
    "subdomain_then_header",
]
