"""
Identity provider abstractions and OAuth2/OIDC builder.

Uses IdentityProvidersConfiguration from from fast_platform. Optional: install
fast_identity[oauth] for httpx-based token/userinfo requests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from from fast_platform import IdentityProvidersConfiguration

try:
    import httpx
except Exception:  # pragma: no cover - optional
    httpx = None  # type: ignore

try:
    from loguru import logger
except Exception:
    logger = None  # type: ignore


@dataclass
class IdentityUserProfile:
    """Normalized identity information returned from providers."""

    subject: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    raw: Dict[str, Any] | None = None


class IIdentityProvider:
    """Minimal interface all concrete identity providers must implement."""

    name: str

    async def build_authorization_url(self, state: str) -> str:  # pragma: no cover
        raise NotImplementedError

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:  # pragma: no cover
        raise NotImplementedError

    async def fetch_user_profile(self, access_token: str) -> IdentityUserProfile:  # pragma: no cover
        raise NotImplementedError


class _OAuth2Provider(IIdentityProvider):
    """Shared OAuth2/OIDC implementation used by concrete providers."""

    def __init__(
        self,
        name: str,
        client_id: str,
        client_secret: str,
        auth_url: str,
        token_url: str,
        userinfo_url: str,
        redirect_uri: str,
        scopes: list[str],
    ) -> None:
        self.name = name
        self._client_id = client_id
        self._client_secret = client_secret
        self._auth_url = auth_url
        self._token_url = token_url
        self._userinfo_url = userinfo_url
        self._redirect_uri = redirect_uri
        self._scopes = scopes

    async def build_authorization_url(self, state: str) -> str:
        from urllib.parse import urlencode

        query = urlencode(
            {
                "client_id": self._client_id,
                "response_type": "code",
                "redirect_uri": self._redirect_uri,
                "scope": " ".join(self._scopes),
                "state": state,
            }
        )
        return f"{self._auth_url}?{query}"

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        if httpx is None:
            raise RuntimeError("httpx is required for OAuth2 flows. Install fast_identity[oauth].")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self._token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self._redirect_uri,
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                },
                headers={"Accept": "application/json"},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()

    async def fetch_user_profile(self, access_token: str) -> IdentityUserProfile:
        if httpx is None:
            raise RuntimeError("httpx is required for OAuth2 flows. Install fast_identity[oauth].")

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                self._userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

        subject = str(data.get("sub") or data.get("id") or "")
        return IdentityUserProfile(
            subject=subject,
            email=data.get("email"),
            name=data.get("name") or data.get("login"),
            picture=data.get("picture"),
            raw=data,
        )


def build_identity_providers() -> dict[str, IIdentityProvider]:
    """
    Construct provider instances from IdentityProvidersConfiguration.

    Only enabled providers with required minimal configuration are instantiated.
    """
    cfg = IdentityProvidersConfiguration.instance().get_config()
    providers: dict[str, IIdentityProvider] = {}

    def _add_oauth2(
        key: str,
        dto: Any,
        default_auth_url: str | None = None,
        default_token_url: str | None = None,
        default_userinfo_url: str | None = None,
    ) -> None:
        if not getattr(dto, "enabled", False):
            return
        auth_url = getattr(dto, "auth_url", None) or default_auth_url
        token_url = getattr(dto, "token_url", None) or default_token_url
        userinfo_url = getattr(dto, "userinfo_url", None) or default_userinfo_url
        client_id = getattr(dto, "client_id", None)
        client_secret = getattr(dto, "client_secret", None)
        if not (client_id and client_secret and auth_url and token_url and userinfo_url):
            if logger:
                logger.warning(
                    "Identity provider {} is enabled but missing required configuration",
                    key,
                )
            return
        providers[key] = _OAuth2Provider(
            name=key,
            client_id=client_id,
            client_secret=client_secret,
            auth_url=auth_url,
            token_url=token_url,
            userinfo_url=userinfo_url,
            redirect_uri=getattr(dto, "redirect_uri", None) or "",
            scopes=list(getattr(dto, "scopes", None) or []),
        )

    _add_oauth2(
        "google",
        cfg.google,
        default_auth_url="https://accounts.google.com/o/oauth2/v2/auth",
        default_token_url="https://oauth2.googleapis.com/token",
        default_userinfo_url="https://openidconnect.googleapis.com/v1/userinfo",
    )
    _add_oauth2(
        "github",
        cfg.github,
        default_auth_url="https://github.com/login/oauth/authorize",
        default_token_url="https://github.com/login/oauth/access_token",
        default_userinfo_url="https://api.github.com/user",
    )
    _add_oauth2("azure_ad", cfg.azure_ad)
    _add_oauth2("okta", cfg.okta)
    _add_oauth2("auth0", cfg.auth0)

    if getattr(cfg.saml, "enabled", False) and logger:
        logger.warning(
            "SAML provider is enabled but the built-in implementation is a "
            "placeholder. Integrate a SAML library for full support.",
        )

    return providers
