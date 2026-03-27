"""Core Edge Functions implementation."""

from enum import Enum
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from functools import wraps
import json
import time
from pydantic import BaseModel


class EdgeRuntime(str, Enum):
    """Runtime environments for edge functions."""

    V8 = "v8"  # JavaScript/WebAssembly
    PYTHON_WASM = "pywasm"  # Python compiled to WASM
    NATIVE = "native"  # Native Python (limited regions)


class GeoLocation(BaseModel):
    """Geographic location information."""

    country_code: str  # "US", "JP", etc.
    country_name: str  # "United States"
    region: Optional[str] = None  # "California"
    city: Optional[str] = None  # "San Francisco"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: Optional[str] = None  # "America/Los_Angeles"
    continent: Optional[str] = None  # "NA"


class EdgeRequest(BaseModel):
    """Request object available in edge functions."""

    url: str
    method: str = "GET"
    headers: Dict[str, str] = {}
    body: Optional[bytes] = None

    # Geo information
    geo: Optional[GeoLocation] = None
    edge_region: Optional[str] = None  # "ap-northeast-1"
    edge_node_id: Optional[str] = None  # Unique node identifier

    # Client info
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None

    # Cache
    cache_status: Optional[str] = None  # "HIT", "MISS", "BYPASS"

    @property
    def json_body(self) -> Any:
        """Parse JSON body."""
        if self.body:
            return json.loads(self.body)
        return None


class EdgeResponse(BaseModel):
    """Response from edge function."""

    status: int = 200
    headers: Dict[str, str] = {}
    body: Optional[bytes] = None

    # Edge caching
    cache_ttl: Optional[int] = None  # Seconds to cache
    cache_tags: List[str] = []  # Cache invalidation tags
    vary_by: List[str] = []  # Vary cache by headers

    @classmethod
    def json(cls, data: Any, status: int = 200, **kwargs) -> "EdgeResponse":
        """Create JSON response."""
        body = json.dumps(data).encode()
        headers = {"content-type": "application/json"}
        headers.update(kwargs.pop("headers", {}))
        return cls(status=status, headers=headers, body=body, **kwargs)

    @classmethod
    def html(cls, content: str, status: int = 200, **kwargs) -> "EdgeResponse":
        """Create HTML response."""
        headers = {"content-type": "text/html"}
        headers.update(kwargs.pop("headers", {}))
        return cls(status=status, headers=headers, body=content.encode(), **kwargs)

    @classmethod
    def text(cls, content: str, status: int = 200, **kwargs) -> "EdgeResponse":
        """Create text response."""
        headers = {"content-type": "text/plain"}
        headers.update(kwargs.pop("headers", {}))
        return cls(status=status, headers=headers, body=content.encode(), **kwargs)

    @classmethod
    def redirect(cls, url: str, status: int = 302) -> "EdgeResponse":
        """Create redirect response."""
        return cls(status=status, headers={"location": url})


@dataclass
class EdgeFunction:
    """Metadata for an edge function."""

    name: str
    handler: Callable
    runtime: EdgeRuntime
    regions: List[str]
    ttl: Optional[int]
    memory_limit_mb: int
    timeout_ms: int
    deploy_config: Dict[str, Any] = field(default_factory=dict)

    async def invoke(self, request: EdgeRequest) -> EdgeResponse:
        """Invoke the edge function."""
        import asyncio

        start_time = time.time()

        try:
            # Execute with timeout
            if asyncio.iscoroutinefunction(self.handler):
                response = await asyncio.wait_for(
                    self.handler(request), timeout=self.timeout_ms / 1000
                )
            else:
                response = self.handler(request)

            # Ensure it's an EdgeResponse
            if not isinstance(response, EdgeResponse):
                if isinstance(response, dict):
                    response = EdgeResponse.json(response)
                elif isinstance(response, str):
                    response = EdgeResponse.text(response)
                else:
                    response = EdgeResponse.json({"result": str(response)})

            # Add edge headers
            response.headers["x-edge-function"] = self.name
            response.headers["x-edge-region"] = request.edge_region or "unknown"
            response.headers["x-edge-processing-time"] = str(int((time.time() - start_time) * 1000))

            return response

        except asyncio.TimeoutError:
            return EdgeResponse.json(
                {"error": "Edge function timeout", "function": self.name}, status=504
            )
        except Exception as e:
            return EdgeResponse.json({"error": str(e), "edge_function": self.name}, status=500)


class EdgeFunctionRegistry:
    """Registry for edge functions."""

    _functions: Dict[str, EdgeFunction] = {}

    @classmethod
    def register(cls, func: EdgeFunction) -> None:
        """Execute register operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """
        cls._functions[func.name] = func

    @classmethod
    def get(cls, name: str) -> Optional[EdgeFunction]:
        """Execute get operation.

        Args:
            name: The name parameter.

        Returns:
            The result of the operation.
        """
        return cls._functions.get(name)

    @classmethod
    def list_all(cls) -> List[EdgeFunction]:
        """Execute list_all operation.

        Returns:
            The result of the operation.
        """
        return list(cls._functions.values())

    @classmethod
    def clear(cls) -> None:
        """Execute clear operation.

        Returns:
            The result of the operation.
        """
        cls._functions.clear()


def edge_function(
    runtime: EdgeRuntime = EdgeRuntime.V8,
    regions: Optional[List[str]] = None,
    ttl: Optional[int] = None,
    memory_limit_mb: int = 128,
    timeout_ms: int = 5000,
    deploy_config: Optional[Dict[str, Any]] = None,
):
    """Decorator to define an edge function.

    Args:
        runtime: Runtime environment (V8, PYTHON_WASM, NATIVE)
        regions: List of edge regions to deploy to
        ttl: Cache TTL in seconds
        memory_limit_mb: Memory limit for function execution
        timeout_ms: Execution timeout in milliseconds
        deploy_config: Additional deployment configuration

    """

    def decorator(func: Callable) -> Callable:
        """Execute decorator operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """
        name = func.__name__

        edge_func = EdgeFunction(
            name=name,
            handler=func,
            runtime=runtime,
            regions=regions or ["all"],
            ttl=ttl,
            memory_limit_mb=memory_limit_mb,
            timeout_ms=timeout_ms,
            deploy_config=deploy_config or {},
        )

        EdgeFunctionRegistry.register(edge_func)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            """Execute wrapper operation.

            Returns:
                The result of the operation.
            """
            return await func(*args, **kwargs)

        wrapper._edge_function = edge_func
        wrapper._is_edge_function = True
        return wrapper

    return decorator


# Built-in edge functions


@edge_function(ttl=300)
async def health_check(request: EdgeRequest) -> EdgeResponse:
    """Health check edge function."""
    return EdgeResponse.json(
        {"status": "healthy", "region": request.edge_region, "timestamp": time.time()}
    )


@edge_function()
async def geo_info(request: EdgeRequest) -> EdgeResponse:
    """Return geo information about the request."""
    return EdgeResponse.json(
        {
            "geo": request.geo.dict() if request.geo else None,
            "edge_region": request.edge_region,
            "client_ip": request.client_ip,
        }
    )
