"""Cost Optimization Recommendations."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from decimal import Decimal

from .core import ResourceType


@dataclass
class OptimizationRecommendation:
    """Cost optimization suggestion."""

    id: str
    title: str
    description: str
    resource_type: ResourceType
    current_cost: Decimal
    potential_savings: Decimal
    confidence: float
    effort: str
    action: str

    @property
    def savings_percentage(self) -> float:
        """Calculate savings percentage."""
        if self.current_cost == 0:
            return 0.0
        return float(self.potential_savings / self.current_cost * 100)


class CostOptimizer:
    """Generate cost optimization recommendations."""

    async def analyze(self, tenant_id: Optional[str] = None) -> List[OptimizationRecommendation]:
        """Analyze costs and generate recommendations."""
        recommendations = []

        # Analyze each resource type
        recommendations.extend(await self._analyze_compute(tenant_id))
        recommendations.extend(await self._analyze_storage(tenant_id))
        recommendations.extend(await self._analyze_cache(tenant_id))

        # Sort by potential savings
        recommendations.sort(key=lambda r: r.potential_savings, reverse=True)

        return recommendations

    async def _analyze_compute(self, tenant_id: Optional[str]) -> List[OptimizationRecommendation]:
        """Analyze compute costs."""
        recommendations = []

        # Get compute metrics
        metrics = await MetricsService.get_compute_utilization(tenant_id)

        for service, utilization in metrics.items():
            if utilization < 0.2:  # < 20% utilization
                current_cost = await self._get_service_cost(service, ResourceType.COMPUTE)

                recommendations.append(
                    OptimizationRecommendation(
                        id=f"compute-downsize-{service}",
                        title=f"Downsize {service}",
                        description=f"Utilization is only {utilization * 100:.1f}%",
                        resource_type=ResourceType.COMPUTE,
                        current_cost=current_cost,
                        potential_savings=current_cost * Decimal("0.5"),
                        confidence=0.9,
                        effort="low",
                        action=f"kubectl scale deployment {service} --replicas=1",
                    )
                )

        return recommendations

    async def _analyze_storage(self, tenant_id: Optional[str]) -> List[OptimizationRecommendation]:
        """Analyze storage costs."""
        recommendations = []

        # Find old data that could be archived
        old_data = await DataAnalyzer.find_old_data(age_threshold_days=365, tenant_id=tenant_id)

        if old_data.get("size_gb", 0) > 100:
            current_cost = old_data.get("current_cost", Decimal("0"))

            recommendations.append(
                OptimizationRecommendation(
                    id="storage-archive",
                    title="Archive old data to cold storage",
                    description=f"{old_data['size_gb']} GB of data older than 1 year",
                    resource_type=ResourceType.STORAGE,
                    current_cost=current_cost,
                    potential_savings=current_cost * Decimal("0.7"),
                    confidence=0.8,
                    effort="medium",
                    action="fastmvc storage archive --age 365d --to s3-glacier",
                )
            )

        return recommendations

    async def _analyze_cache(self, tenant_id: Optional[str]) -> List[OptimizationRecommendation]:
        """Analyze cache costs."""
        recommendations = []

        # Check for oversized caches
        cache_metrics = await MetricsService.get_cache_metrics(tenant_id)

        for cache_name, metrics in cache_metrics.items():
            hit_rate = metrics.get("hit_rate", 0)
            if hit_rate < 0.3:  # < 30% hit rate
                current_cost = await self._get_service_cost(cache_name, ResourceType.CACHE)

                recommendations.append(
                    OptimizationRecommendation(
                        id=f"cache-downsize-{cache_name}",
                        title=f"Downsize cache: {cache_name}",
                        description=f"Hit rate is only {hit_rate * 100:.1f}%",
                        resource_type=ResourceType.CACHE,
                        current_cost=current_cost,
                        potential_savings=current_cost * Decimal("0.4"),
                        confidence=0.8,
                        effort="low",
                        action=f"redis-cli --cluster resize {cache_name} --nodes 3",
                    )
                )

        return recommendations

    async def _get_service_cost(self, service: str, resource_type: ResourceType) -> Decimal:
        """Get cost for a service."""
        # Placeholder - would query cost database
        return Decimal("100.00")


# Mock services for development


class MetricsService:
    """Mock metrics service."""

    @staticmethod
    async def get_compute_utilization(tenant_id: Optional[str]) -> Dict[str, float]:
        """Get compute utilization by service."""
        return {
            "api-service": 0.15,
            "worker-service": 0.45,
            "background-jobs": 0.08,
        }

    @staticmethod
    async def get_cache_metrics(tenant_id: Optional[str]) -> Dict[str, Dict[str, Any]]:
        """Get cache metrics."""
        return {
            "session-cache": {"hit_rate": 0.25, "size_mb": 512},
            "query-cache": {"hit_rate": 0.65, "size_mb": 1024},
        }


class DataAnalyzer:
    """Mock data analyzer."""

    @staticmethod
    async def find_old_data(age_threshold_days: int, tenant_id: Optional[str]) -> Dict[str, Any]:
        """Find old data that could be archived."""
        return {
            "size_gb": 150,
            "current_cost": Decimal("150.00"),
            "tables": ["logs", "events", "metrics"],
        }
