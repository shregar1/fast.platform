"""Edge KV (Key-Value) Store."""

from typing import Optional, Any, List
import json
import hashlib
import time


class EdgeKV:
    """Key-Value store at the edge
    Replicated across edge locations.

    In production, this uses Cloudflare Workers KV, Fastly Edge Dictionary,
    or similar edge-native storage.
    """

    # In-memory storage for development/testing
    _stores: dict = {}

    def __init__(self, namespace: str):
        """Execute __init__ operation.

        Args:
            namespace: The namespace parameter.
        """
        self.namespace = namespace
        if namespace not in self._stores:
            self._stores[namespace] = {}

    def _namespaced_key(self, key: str) -> str:
        """Execute _namespaced_key operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        return f"{self.namespace}:{key}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from edge KV."""
        ns_key = self._namespaced_key(key)
        store = self._stores[self.namespace]

        if ns_key not in store:
            return None

        entry = store[ns_key]

        # Check TTL
        if entry.get("expires") and entry["expires"] < time.time():
            del store[ns_key]
            return None

        return entry["value"]

    async def get_with_metadata(self, key: str) -> Optional[dict]:
        """Get value with metadata."""
        ns_key = self._namespaced_key(key)
        store = self._stores[self.namespace]

        if ns_key not in store:
            return None

        entry = store[ns_key]

        if entry.get("expires") and entry["expires"] < time.time():
            del store[ns_key]
            return None

        return {"value": entry["value"], "created": entry.get("created"), "ttl": entry.get("ttl")}

    async def put(
        self, key: str, value: Any, ttl: Optional[int] = None, metadata: Optional[dict] = None
    ) -> None:
        """Put value to edge KV."""
        ns_key = self._namespaced_key(key)
        store = self._stores[self.namespace]

        entry = {"value": value, "created": time.time(), "metadata": metadata or {}}

        if ttl:
            entry["expires"] = time.time() + ttl
            entry["ttl"] = ttl

        store[ns_key] = entry

    async def delete(self, key: str) -> bool:
        """Delete key from edge KV."""
        ns_key = self._namespaced_key(key)
        store = self._stores[self.namespace]

        if ns_key in store:
            del store[ns_key]
            return True
        return False

    async def list_keys(self, prefix: str = "") -> List[str]:
        """List keys with prefix."""
        store = self._stores[self.namespace]
        prefix_full = self._namespaced_key(prefix)

        keys = []
        for key in store.keys():
            if key.startswith(prefix_full):
                # Remove namespace prefix
                clean_key = key[len(self.namespace) + 1 :]
                keys.append(clean_key)

        return keys

    async def list(self, prefix: str = "") -> List[str]:
        """Alias for list_keys."""
        return await self.list_keys(prefix)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        value = await self.get(key)
        return value is not None

    async def increment(self, key: str, amount: int = 1) -> int:
        """Atomically increment a counter."""
        current = await self.get(key)
        if current is None:
            current = 0
        new_value = current + amount
        await self.put(key, new_value)
        return new_value

    async def decrement(self, key: str, amount: int = 1) -> int:
        """Atomically decrement a counter."""
        return await self.increment(key, -amount)

    async def clear(self) -> None:
        """Clear all keys in namespace."""
        self._stores[self.namespace] = {}
