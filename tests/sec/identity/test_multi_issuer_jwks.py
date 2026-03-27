"""Tests for MultiIssuerJWKSCache."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sec.identity.multi_issuer_jwks import MultiIssuerJWKSCache
from tests.sec.identity.abstraction import IIdentityTests


class TestMultiIssuerJwks(IIdentityTests):
    """Represents the TestMultiIssuerJwks class."""

    def test_multi_issuer_routes(self):
        """Execute test_multi_issuer_routes operation.

        Returns:
            The result of the operation.
        """
        jwks_a = {"keys": [{"kid": "a"}]}
        jwks_b = {"keys": [{"kid": "b"}]}

        async def run():
            """Execute run operation.

            Returns:
                The result of the operation.
            """
            reg = MultiIssuerJWKSCache(
                {
                    "https://old-idp/": "https://old-idp/jwks.json",
                    "https://new-idp/": "https://new-idp/jwks.json",
                },
                ttl_seconds=60,
            )
            assert reg.has_issuer("https://old-idp/")
            assert "https://new-idp/" in reg.issuers()
            calls = []

            def make_resp(data):
                """Execute make_resp operation.

                Args:
                    data: The data parameter.

                Returns:
                    The result of the operation.
                """
                mock_resp = MagicMock()
                mock_resp.json.return_value = data
                mock_resp.raise_for_status = MagicMock()
                return mock_resp

            mock_cm = AsyncMock()

            async def mock_get(url, **kwargs):
                """Execute mock_get operation.

                Args:
                    url: The url parameter.

                Returns:
                    The result of the operation.
                """
                calls.append(url)
                if "old-idp" in url:
                    return make_resp(jwks_a)
                return make_resp(jwks_b)

            mock_cm.__aenter__.return_value.get = AsyncMock(side_effect=mock_get)
            mock_cm.__aexit__.return_value = None
            with patch("sec.identity.jwks_cache.httpx.AsyncClient", return_value=mock_cm):
                assert await reg.get_jwks("https://old-idp/") == jwks_a
                assert await reg.get_jwks("https://new-idp/") == jwks_b
            assert "https://old-idp/jwks.json" in calls
            assert "https://new-idp/jwks.json" in calls

        asyncio.run(run())

    def test_multi_issuer_unknown_raises(self):
        """Execute test_multi_issuer_unknown_raises operation.

        Returns:
            The result of the operation.
        """

        async def run():
            """Execute run operation.

            Returns:
                The result of the operation.
            """
            reg = MultiIssuerJWKSCache({"https://a/": "https://a/jwks.json"})
            with pytest.raises(KeyError):
                await reg.get_jwks("https://other/")

        asyncio.run(run())

    def test_multi_issuer_empty_map_rejected(self):
        """Execute test_multi_issuer_empty_map_rejected operation.

        Returns:
            The result of the operation.
        """
        with pytest.raises(ValueError):
            MultiIssuerJWKSCache({})

    def test_refresh_issuer_unknown_raises(self):
        """Execute test_refresh_issuer_unknown_raises operation.

        Returns:
            The result of the operation.
        """

        async def run():
            """Execute run operation.

            Returns:
                The result of the operation.
            """
            reg = MultiIssuerJWKSCache({"https://a/": "https://a/jwks.json"})
            with pytest.raises(KeyError):
                await reg.refresh_issuer("https://other/")

        asyncio.run(run())
