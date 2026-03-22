"""Tests for JWKSCache."""
from tests.sec.identity.abstraction import IIdentityTests


import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from identity.jwks_cache import JWKSCache

@pytest.fixture
def sample_jwks():
    return {"keys": [{"kty": "RSA", "kid": "a", "n": "x", "e": "AQAB"}]}


class TestJwksCache(IIdentityTests):

    def test_jwks_cache_fetch_and_ttl(self, monkeypatch, sample_jwks):

        async def run():
            cache = JWKSCache('https://idp/.well-known/jwks.json', ttl_seconds=3600)
            mock_resp = MagicMock()
            mock_resp.json.return_value = sample_jwks
            mock_resp.raise_for_status = MagicMock()
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value.get = AsyncMock(return_value=mock_resp)
            mock_cm.__aexit__.return_value = None
            with patch('identity.jwks_cache.httpx.AsyncClient', return_value=mock_cm):
                j1 = await cache.get_jwks()
                j2 = await cache.get_jwks()
            assert j1 == sample_jwks
            assert j2 == sample_jwks
            assert mock_cm.__aenter__.return_value.get.await_count == 1
        asyncio.run(run())

    def test_jwks_refresh_forces_fetch(self, sample_jwks):

        async def run():
            cache = JWKSCache('https://idp/jwks', ttl_seconds=99999)
            mock_resp = MagicMock()
            mock_resp.json.return_value = sample_jwks
            mock_resp.raise_for_status = MagicMock()
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value.get = AsyncMock(return_value=mock_resp)
            mock_cm.__aexit__.return_value = None
            with patch('identity.jwks_cache.httpx.AsyncClient', return_value=mock_cm):
                await cache.get_jwks()
                await cache.refresh()
            assert mock_cm.__aenter__.return_value.get.await_count == 2
        asyncio.run(run())

    def test_jwks_non_object_json_raises(self):

        async def run():
            cache = JWKSCache('https://idp/jwks', ttl_seconds=1)
            mock_resp = MagicMock()
            mock_resp.json.return_value = ['not', 'dict']
            mock_resp.raise_for_status = MagicMock()
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value.get = AsyncMock(return_value=mock_resp)
            mock_cm.__aexit__.return_value = None
            with patch('identity.jwks_cache.httpx.AsyncClient', return_value=mock_cm):
                with pytest.raises(ValueError, match='JSON object'):
                    await cache.get_jwks()
        asyncio.run(run())
