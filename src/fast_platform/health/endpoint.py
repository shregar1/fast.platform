"""Health check HTTP endpoint."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Response, status

from .checks import HealthCheck, HealthResult, HealthStatus


class HealthEndpoint:
    """FastAPI endpoint for health checks."""

    def __init__(
        self, prefix: str = "/health", include_details: bool = True, cache_seconds: float = 5.0
    ):
        """Execute __init__ operation.

        Args:
            prefix: The prefix parameter.
            include_details: The include_details parameter.
            cache_seconds: The cache_seconds parameter.
        """
        self.prefix = prefix
        self.include_details = include_details
        self.cache_seconds = cache_seconds
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_time: float = 0

    def create_router(self) -> APIRouter:
        """Create FastAPI router with health endpoints."""
        router = APIRouter(prefix=self.prefix)

        @router.get("/health")
        async def health() -> Response:
            """General health check."""
            results = await HealthCheck.run_checks("health")
            overall = HealthCheck.get_overall_status(results)

            status_code = (
                status.HTTP_200_OK
                if overall == HealthStatus.HEALTHY
                else status.HTTP_503_SERVICE_UNAVAILABLE
            )

            body = self._format_response(results, overall)
            return Response(content=body, status_code=status_code, media_type="application/json")

        @router.get("/ready")
        async def ready() -> Response:
            """Kubernetes readiness probe."""
            results = await HealthCheck.run_checks("ready")
            is_ready = all(
                r.status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED) for r in results
            )

            status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE

            body = self._format_response(
                results, HealthStatus.HEALTHY if is_ready else HealthStatus.UNHEALTHY
            )
            return Response(content=body, status_code=status_code, media_type="application/json")

        @router.get("/live")
        async def live() -> Response:
            """Kubernetes liveness probe."""
            results = await HealthCheck.run_checks("live")
            is_alive = all(r.status != HealthStatus.UNHEALTHY for r in results)

            status_code = status.HTTP_200_OK if is_alive else status.HTTP_503_SERVICE_UNAVAILABLE

            return Response(
                content='{"status": "alive"}',
                status_code=status_code,
                media_type="application/json",
            )

        @router.get("/startup")
        async def startup() -> Response:
            """Kubernetes startup probe."""
            results = await HealthCheck.run_checks("startup")
            overall = HealthCheck.get_overall_status(results)

            status_code = (
                status.HTTP_200_OK
                if overall != HealthStatus.UNHEALTHY
                else status.HTTP_503_SERVICE_UNAVAILABLE
            )

            body = self._format_response(results, overall)
            return Response(content=body, status_code=status_code, media_type="application/json")

        return router

    def _format_response(self, results: list, overall: HealthStatus) -> str:
        """Format health check response."""
        import json

        response = {"status": overall.value, "timestamp": datetime.utcnow().isoformat()}

        if self.include_details:
            response["checks"] = [r.to_dict() for r in results]

        return json.dumps(response)


def create_health_endpoint(prefix: str = "/health", include_details: bool = True) -> APIRouter:
    """Convenience function to create health endpoint router."""
    endpoint = HealthEndpoint(prefix=prefix, include_details=include_details)
    return endpoint.create_router()


from datetime import datetime
