# Smart Caching System

The Smart Caching System provides production-grade caching with cache-aside pattern, stale-while-revalidate, request deduplication, and event-based invalidation.

> **Canonical location:** this guide lives in `fast_platform/src/fast_platform/caching/README.md` alongside the `fast_platform.caching` package.

## Overview

```python
from fast_platform.caching import smart_cache

@smart_cache.cached(
    ttl=300,              # Cache for 5 minutes
    stale_ttl=60,         # Serve stale for 1 minute while refreshing
    invalidate_on=["user:update", "user:delete"]
)
async def get_user(user_id: str) -> User:
    return await db.query(User).get(user_id)
```

## Features

| Feature | Description |
| --- | --- |
| **Cache-Aside Pattern** | Application manages cache, transparent get/set |
| **Stale-While-Revalidate** | Serve stale data while refreshing in background |
| **Request Deduplication** | Thundering herd protection - concurrent requests for same cache miss are collapsed into one |
| **Event-Based Invalidation** | Auto-invalidate cache on specific events |
| **Compression** | Automatic compression for large values |
| **Multi-Level** | L1 (local) + L2 (Redis) support |

## Basic Usage

### Using the Decorator

```python
from fast_platform.caching import smart_cache

@smart_cache.cached(ttl=300)
async def get_user(user_id: str) -> User:
    """Get user with automatic caching."""
    return await db.query(User).get(user_id)

@smart_cache.cached(
    ttl=600,
    key_prefix="products",
    tags=["catalog"]
)
async def get_products(category: str) -> List[Product]:
    """Get products with 10-minute cache."""
    return await db.query(Product).filter_by(category=category).all()
```

### Manual Cache Operations

```python
from fast_platform.caching import smart_cache

# Set a value
await smart_cache.set("key", value, ttl=300)

# Get a value
value = await smart_cache.get("key")

# Get or compute
result = await smart_cache.get_or_set(
    "expensive_key",
    factory=lambda: expensive_computation(),
    ttl=300
)

# Delete a key
await smart_cache.delete("key")

# Delete by pattern
await smart_cache.delete_pattern("user:*")

# Clear all cache
await smart_cache.clear()
```

## Stale-While-Revalidate

Serve stale data while refreshing in the background - zero downtime cache updates:

```python
@smart_cache.cached(
    ttl=300,        # Fresh for 5 minutes
    stale_ttl=60    # Serve stale for 1 additional minute while refreshing
)
async def get_dashboard_data() -> DashboardData:
    """
    Returns cached data immediately.
    If stale (5-6 minutes old), returns stale data and refreshes in background.
    """
    return await compute_dashboard_data()
```

**How it works:**

1. First request: Computes and caches result
2. Within 5 minutes: Returns cached result
3. 5-6 minutes: Returns stale result, triggers background refresh
4. After 6 minutes: Computes fresh result

## Request Deduplication (Thundering Herd Protection)

When multiple concurrent requests hit a cache miss, only one database query is executed:

```python
# 1000 concurrent requests for the same cache-miss
# = 1 database query
@smart_cache.cached(
    ttl=60,
    request_deduplication=True  # Default
)
async def get_popular_products() -> List[Product]:
    return await db.query(Product).order_by(Product.views.desc()).limit(10).all()
```

## Event-Based Invalidation

Automatically invalidate cache when specific events occur:

```python
@smart_cache.cached(
    ttl=300,
    invalidate_on=[
        "user:update",   # Invalidate when user is updated
        "user:delete",   # Invalidate when user is deleted
        "user:password_change"
    ]
)
async def get_user_profile(user_id: str) -> UserProfile:
    return await fetch_user_profile(user_id)

# Elsewhere in your code:
from fast_platform.caching import smart_cache
from fast_platform.caching import InvalidationEvent

# Trigger invalidation
event = InvalidationEvent(
    event_type="update",
    resource_type="user",
    resource_id="user_123"
)
await smart_cache.handle_invalidation_event(event)
```

## Conditional Caching

Only cache values that meet certain conditions:

```python
def should_cache(result):
    """Only cache successful results with data."""
    return result is not None and len(result) > 0

@smart_cache.cached(
    ttl=300,
    condition=should_cache
)
async def search_products(query: str) -> List[Product]:
    return await perform_search(query)
```

## Cache Configuration

### Global Configuration

```python
from fast_platform.caching import CacheConfig, SmartCacheManager

config = CacheConfig(
    default_ttl_seconds=300,
    stale_while_revalidate_seconds=60,
    max_size=10000,
    compression_enabled=True,
    compression_threshold_bytes=1024,
    request_deduplication=True,
    dedup_window_seconds=5.0
)

cache = SmartCacheManager(config=config)
```

### Using Redis Backend

```python
from fast_platform.caching import CacheConfig, SmartCacheManager
from fast_platform.caching import RedisCacheBackend

redis_backend = RedisCacheBackend(
    host="localhost",
    port=6379,
    db=0
)

cache = SmartCacheManager(
    config=CacheConfig(),
    backend=redis_backend
)
```

## Cache Statistics

Monitor cache performance:

```python
from fast_platform.caching import smart_cache

stats = smart_cache.get_stats()
print(f"""
Cache Statistics:
  Hits: {stats['hits']}
  Misses: {stats['misses']}
  Stale Hits: {stats['stale_hits']}
  Deduplicated: {stats['deduplicated']}
  Hit Rate: {stats['hit_rate_formatted']}
""")
```

## Cache Invalidation

### Manual Invalidation

```python
from fast_platform.caching import cache_invalidator

# Invalidate by resource type
await cache_invalidator.invalidate_resource("user", resource_id="123")

# Invalidate by tenant
await cache_invalidator.invalidate_tenant("tenant_abc")

# Invalidate by user
await cache_invalidator.invalidate_user("user_123")

# Pattern-based invalidation
await smart_cache.delete_pattern("products:category:*")
```

### Automatic Invalidation with Decorators

```python
from fast_platform.caching import smart_cache

class UserService:
    @smart_cache.cached(
        ttl=300,
        invalidate_on=["user:update"]
    )
    async def get_user(self, user_id: str) -> User:
        return await self.repository.get(user_id)
    
    async def update_user(self, user_id: str, data: dict) -> User:
        user = await self.repository.update(user_id, data)
        
        # Invalidate cache
        await smart_cache.delete_pattern(f"user:{user_id}*")
        
        return user
```

## Advanced Patterns

### Multi-Key Dependencies

```python
@smart_cache.cached(
    ttl=300,
    invalidate_on=[
        "user:update",
        "order:create",
        "order:update"
    ]
)
async def get_user_dashboard(user_id: str) -> Dashboard:
    """Invalidated when user or their orders change."""
    user = await get_user(user_id)
    orders = await get_user_orders(user_id)
    return Dashboard(user=user, orders=orders)
```

### Cache Warming

```python
async def warm_cache():
    """Pre-populate cache on startup."""
    popular_users = await get_popular_users()
    
    for user in popular_users:
        await smart_cache.get_or_set(
            f"user:{user.id}",
            lambda u=user: fetch_user_data(u.id),
            ttl=300
        )
```

### Circuit Breaker Integration

```python
from fast_platform.caching import smart_cache
from fast_platform.core.database import CircuitBreaker

circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30
)

@smart_cache.cached(ttl=60)
async def get_external_data():
    if circuit_breaker.is_open():
        # Return cached stale data if available
        return await smart_cache.get("external_data:stale")
    
    try:
        data = await fetch_from_external_api()
        circuit_breaker.record_success()
        return data
    except Exception as e:
        circuit_breaker.record_failure()
        raise
```

## Best Practices

### 1. Choose Appropriate TTL

```python
# Short TTL for frequently changing data
@smart_cache.cached(ttl=60)
async def get_stock_price(symbol: str) -> float:
    pass

# Long TTL for static data
@smart_cache.cached(ttl=3600)
async def get_product_catalog() -> List[Product]:
    pass
```

### 2. Use Tags for Bulk Invalidation

```python
@smart_cache.cached(
    ttl=300,
    tags=["products", "category:electronics"]
)
async def get_electronics() -> List[Product]:
    pass

# Later: invalidate all products
await smart_cache.delete_pattern("*category:electronics*")
```

### 3. Handle Cache Misses Gracefully

```python
@smart_cache.cached(ttl=300)
async def get_critical_data():
    try:
        return await fetch_from_database()
    except Exception:
        # Try to get stale data
        stale = await smart_cache.get("key:stale")
        if stale:
            return stale
        raise
```

### 4. Monitor Hit Rates

```python
# Log cache metrics periodically
async def log_cache_metrics():
    stats = smart_cache.get_stats()
    if stats['hit_rate'] < 0.5:
        logger.warning(f"Low cache hit rate: {stats['hit_rate_formatted']}")
```

## API Reference

### SmartCacheManager

```python
class SmartCacheManager:
    def __init__(
        self,
        config: Optional[CacheConfig] = None,
        backend: Optional[CacheBackend] = None
    )
    
    async def get(self, key: str) -> Optional[Any]
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        stale_ttl: Optional[int] = None
    ) -> bool
    async def delete(self, key: str) -> bool
    async def delete_pattern(self, pattern: str) -> int
    async def get_or_set(
        self,
        key: str,
        factory: Callable,
        ttl: Optional[int] = None,
        stale_ttl: Optional[int] = None
    ) -> Any
    def cached(
        self,
        ttl: Optional[int] = None,
        stale_ttl: Optional[int] = None,
        key_prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        condition: Optional[Callable[[Any], bool]] = None,
        invalidate_on: Optional[List[str]] = None
    ) -> Callable
    def get_stats(self) -> Dict[str, Any]
```

## Related Topics

- [N+1 Detection](../../../../docs/features/nplus1-detection.md) - Optimize database queries
- [Distributed Tracing](../../../../docs/features/distributed-tracing.md) - Monitor cache performance
- [Configuration](../../../../docs/guide/configuration.md) - Cache configuration options
