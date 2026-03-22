"""
Named tenant resolution strategies and a registry for building resolvers.

Use this when you want configurable resolution (e.g. subdomain first, then header)
without wiring ``ChainedTenantResolver`` manually in every app.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional, Sequence, Union

from .context import TenantStore
from .middleware import (
    ChainedTenantResolver,
    HeaderTenantResolver,
    JWTTenantResolver,
    PathTenantResolver,
    SubdomainTenantResolver,
    TenantResolver,
)

ResolverFactory = Callable[[TenantStore, dict[str, Any]], TenantResolver]


class ResolutionStrategy(str, Enum):
    """Built-in strategy keys used with :class:`TenantResolverRegistry`."""

    HEADER = "header"
    SUBDOMAIN = "subdomain"
    PATH = "path"
    JWT = "jwt"


@dataclass(frozen=True)
class ResolverSpec:
    """
    One step in a resolution chain: strategy name and options passed to the factory.

    Example::

        ResolverSpec(ResolutionStrategy.SUBDOMAIN, {"base_domain": "app.example.com"})
    """

    strategy: Union[str, ResolutionStrategy]
    options: dict[str, Any] = field(default_factory=dict)


def _normalize_key(name: str) -> str:
    return str(name).strip().lower().replace("-", "_")


def _strategy_key(name: Union[str, ResolutionStrategy]) -> str:
    raw = name.value if isinstance(name, ResolutionStrategy) else str(name)
    return _normalize_key(raw)


class TenantResolverRegistry:
    """
    Registry of named resolution strategies.

    Default registrations: ``header``, ``subdomain``, ``path``, ``jwt``.
    Register custom factories with :meth:`register`.
    """

    def __init__(self) -> None:
        self._factories: dict[str, ResolverFactory] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(
            ResolutionStrategy.HEADER,
            lambda store, opts: HeaderTenantResolver(
                store,
                header_name=opts.get("header_name", "X-Tenant-ID"),
            ),
        )
        self.register(
            ResolutionStrategy.SUBDOMAIN,
            lambda store, opts: SubdomainTenantResolver(
                store,
                base_domain=opts["base_domain"],
                excluded_subdomains=opts.get("excluded_subdomains"),
            ),
        )
        self.register(
            ResolutionStrategy.PATH,
            lambda store, opts: PathTenantResolver(
                store,
                prefix=opts.get("prefix", "/t/"),
            ),
        )
        self.register(
            ResolutionStrategy.JWT,
            lambda store, opts: JWTTenantResolver(
                store,
                claim_name=opts.get("claim_name", "tenant_id"),
            ),
        )

    def register(self, name: Union[str, ResolutionStrategy], factory: ResolverFactory) -> None:
        """Register or replace a strategy factory. Name is normalized (case-insensitive)."""
        self._factories[_strategy_key(name)] = factory

    def unregister(self, name: Union[str, ResolutionStrategy]) -> None:
        """Remove a strategy (mostly for tests)."""
        self._factories.pop(_strategy_key(name), None)

    def list_strategies(self) -> list[str]:
        """Registered strategy keys, sorted."""
        return sorted(self._factories.keys())

    def build(self, store: TenantStore, name: Union[str, ResolutionStrategy], **options: Any) -> TenantResolver:
        """
        Build a single resolver. ``options`` are passed to the strategy factory
        (e.g. ``base_domain=...`` for ``subdomain``).
        """
        key = _strategy_key(name)
        if key not in self._factories:
            raise KeyError(f"Unknown resolution strategy: {name!r}; known: {self.list_strategies()}")
        return self._factories[key](store, options)

    def build_chain(self, store: TenantStore, specs: Sequence[ResolverSpec]) -> ChainedTenantResolver:
        """Build a :class:`ChainedTenantResolver` from ordered :class:`ResolverSpec` entries."""
        resolvers = [self.build(store, s.strategy, **s.options) for s in specs]
        return ChainedTenantResolver(resolvers)


_default_registry: Optional[TenantResolverRegistry] = None


def default_registry() -> TenantResolverRegistry:
    """Shared default registry (lazy singleton)."""
    global _default_registry
    if _default_registry is None:
        _default_registry = TenantResolverRegistry()
    return _default_registry


def subdomain_then_header(
    store: TenantStore,
    *,
    base_domain: str,
    header_name: str = "X-Tenant-ID",
    excluded_subdomains: Optional[list[str]] = None,
) -> ChainedTenantResolver:
    """
    Common preset: resolve by subdomain slug first, then by ``header_name`` (tenant id).

    Subdomain resolution uses :class:`SubdomainTenantResolver`; header uses
    :class:`HeaderTenantResolver`.
    """
    reg = default_registry()
    return reg.build_chain(
        store,
        [
            ResolverSpec(
                ResolutionStrategy.SUBDOMAIN,
                {"base_domain": base_domain, "excluded_subdomains": excluded_subdomains},
            ),
            ResolverSpec(ResolutionStrategy.HEADER, {"header_name": header_name}),
        ],
    )


__all__ = [
    "ResolutionStrategy",
    "ResolverSpec",
    "TenantResolverRegistry",
    "default_registry",
    "subdomain_then_header",
]
