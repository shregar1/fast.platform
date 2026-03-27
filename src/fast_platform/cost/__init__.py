"""FastMVC Cost Tracking Module.

Comprehensive cost visibility, per-tenant attribution, budget alerts, and optimization recommendations.
"""

from .core import (
    ResourceType,
    CloudProvider,
    CostEvent,
    CostContext,
    CostTracker,
    track_costs,
)
from .budget import (
    Budget,
    BudgetAlert,
    BudgetManager,
)
from .optimizer import (
    OptimizationRecommendation,
    CostOptimizer,
)

__all__ = [
    "ResourceType",
    "CloudProvider",
    "CostEvent",
    "CostContext",
    "CostTracker",
    "track_costs",
    "Budget",
    "BudgetAlert",
    "BudgetManager",
    "OptimizationRecommendation",
    "CostOptimizer",
]
