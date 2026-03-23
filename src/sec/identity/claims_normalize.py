"""
Normalize common JWT/OIDC claim shapes (Keycloak ``realm_access``, ``scope``, …)
and step-up context (``amr``, ``acr``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, FrozenSet, Optional


def parse_amr_claim(value: Any) -> FrozenSet[str]:
    """
    Parse Authentication Methods References (RFC 8176 / OIDC ``amr``).

    Accepts ``None``, a string (split on whitespace), or a sequence of strings.
    """
    if value is None:
        return frozenset()
    if isinstance(value, str):
        return frozenset(s for s in value.split() if s)
    if isinstance(value, (list, tuple, set)):
        return frozenset(str(x) for x in value if x is not None and str(x))
    return frozenset((str(value),))


def parse_acr_claim(value: Any) -> Optional[str]:
    """Parse Authentication Context Class Reference (``acr``) as optional string."""
    if value is None:
        return None
    if isinstance(value, str):
        return value if value else None
    return str(value)


def normalize_roles(claims: dict[str, Any]) -> FrozenSet[str]:
    """Collect roles from ``realm_access``, ``resource_access``, and ``roles``."""
    roles: set[str] = set()
    ra = claims.get("realm_access")
    if isinstance(ra, dict):
        r = ra.get("roles")
        if isinstance(r, list):
            roles.update(str(x) for x in r)
    res = claims.get("resource_access")
    if isinstance(res, dict):
        for block in res.values():
            if isinstance(block, dict):
                r = block.get("roles")
                if isinstance(r, list):
                    roles.update(str(x) for x in r)
    direct = claims.get("roles")
    if isinstance(direct, list):
        roles.update(str(x) for x in direct)
    return frozenset(roles)


def normalize_scopes(claims: dict[str, Any]) -> FrozenSet[str]:
    """Collect scopes from ``scope`` (space-separated) or ``scp`` (string or list)."""
    sc = claims.get("scope")
    if isinstance(sc, str) and sc.strip():
        return frozenset(s for s in sc.split() if s)
    scp = claims.get("scp")
    if isinstance(scp, list):
        return frozenset(str(x) for x in scp)
    if isinstance(scp, str) and scp.strip():
        return frozenset(s for s in scp.split() if s)
    return frozenset()


@dataclass(frozen=True)
class NormalizedClaims:
    """Stable view of subject, issuer, audience, roles, scopes, and MFA context."""

    subject: str
    roles: FrozenSet[str] = frozenset()
    scopes: FrozenSet[str] = frozenset()
    issuer: Optional[str] = None
    audience: Optional[str | tuple[str, ...]] = None
    amr: FrozenSet[str] = frozenset()
    acr: Optional[str] = None


def _normalize_aud(aud: Any) -> Optional[str | tuple[str, ...]]:
    if aud is None:
        return None
    if isinstance(aud, str):
        return aud
    if isinstance(aud, list):
        t = tuple(str(x) for x in aud)
        return t if len(t) > 1 else (t[0] if t else None)
    return str(aud)


def normalize_token_claims(claims: dict[str, Any]) -> NormalizedClaims:
    """Build :class:`NormalizedClaims` from a decoded JWT payload dict."""
    sub = claims.get("sub")
    subject = str(sub) if sub is not None else ""
    return NormalizedClaims(
        subject=subject,
        roles=normalize_roles(claims),
        scopes=normalize_scopes(claims),
        issuer=claims.get("iss") if isinstance(claims.get("iss"), str) else None,
        audience=_normalize_aud(claims.get("aud")),
        amr=parse_amr_claim(claims.get("amr")),
        acr=parse_acr_claim(claims.get("acr")),
    )
