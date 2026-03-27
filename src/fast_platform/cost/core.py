"""
Core Cost Tracking implementation
"""

from enum import Enum
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from functools import wraps
from contextvars import ContextVar
import time


class ResourceType(Enum):
    """Types of resources that incur costs"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    CACHE = "cache"
    QUEUE = "queue"
    SEARCH = "search"
    ML_INFERENCE = "ml_inference"
    THIRD_PARTY_API = "third_party_api"


class CloudProvider(Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


@dataclass
class CostEvent:
    """A single cost-generating event"""
    id: str
    timestamp: datetime
    tenant_id: Optional[str]
    resource_type: ResourceType
    resource_id: str
    quantity: Decimal
    unit: str
    unit_cost: Decimal
    total_cost: Decimal
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    endpoint: Optional[str] = None
    tags: Dict[str, Any] = field(default_factory=dict)


# Context variable for current request cost tracking
current_cost_context: ContextVar[Optional["CostContext"]] = ContextVar(
    "cost_context", default=None
)


class CostContext:
    """Tracks costs for current request/operation"""
    
    def __init__(self, tenant_id: Optional[str] = None, request_id: Optional[str] = None):
        from uuid import uuid4
        self.tenant_id = tenant_id
        self.request_id = request_id or str(uuid4())
        self.events: List[CostEvent] = []
        self.start_time = datetime.utcnow()
    
    def record(
        self,
        resource_type: ResourceType,
        quantity: Decimal,
        unit: str,
        resource_id: str,
        **tags
    ) -> CostEvent:
        """Record a cost event"""
        from uuid import uuid4
        
        # Get unit cost from pricing service
        unit_cost = PricingService.get_unit_cost(resource_type, unit)
        
        event = CostEvent(
            id=str(uuid4()),
            timestamp=datetime.utcnow(),
            tenant_id=self.tenant_id,
            resource_type=resource_type,
            resource_id=resource_id,
            quantity=quantity,
            unit=unit,
            unit_cost=unit_cost,
            total_cost=quantity * unit_cost,
            request_id=self.request_id,
            tags=tags
        )
        
        self.events.append(event)
        return event
    
    def get_total(self) -> Decimal:
        """Get total cost for this context"""
        return sum(e.total_cost for e in self.events)
    
    async def flush(self) -> None:
        """Flush events to storage"""
        await CostEventStore.save_many(self.events)
        
        # Update budget
        if self.tenant_id:
            from .budget import BudgetManager
            await BudgetManager.update_spend(self.tenant_id, self.get_total())


class CostTracker:
    """Main interface for cost tracking"""
    
    @staticmethod
    def start_context(
        tenant_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> CostContext:
        """Start a new cost tracking context"""
        ctx = CostContext(tenant_id=tenant_id, request_id=request_id)
        current_cost_context.set(ctx)
        return ctx
    
    @staticmethod
    def get_context() -> Optional[CostContext]:
        """Get current cost context"""
        return current_cost_context.get()
    
    @staticmethod
    def record(
        resource_type: ResourceType,
        quantity: Decimal,
        unit: str,
        resource_id: str,
        **tags
    ) -> Optional[CostEvent]:
        """Record cost in current context"""
        ctx = current_cost_context.get()
        if ctx:
            return ctx.record(resource_type, quantity, unit, resource_id, **tags)
        return None
    
    @staticmethod
    async def flush() -> None:
        """Flush current context"""
        ctx = current_cost_context.get()
        if ctx:
            await ctx.flush()
            current_cost_context.set(None)
    
    @staticmethod
    def get_current_total() -> Decimal:
        """Get total cost of current context"""
        ctx = current_cost_context.get()
        if ctx:
            return ctx.get_total()
        return Decimal("0")


def track_costs(
    resource_type: ResourceType,
    model: str = "per-request",
    tenant_extractor: Optional[Callable] = None
):
    """
    Decorator to automatically track costs for a function
    
    Args:
        resource_type: Type of resource being used
        model: Pricing model ("per-request", "per-second", "per-gb")
        tenant_extractor: Function to extract tenant_id from request
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract tenant
            tenant_id = None
            if tenant_extractor:
                try:
                    result = tenant_extractor(*args, **kwargs)
                    if asyncio.iscoroutinefunction(tenant_extractor):
                        tenant_id = await result
                    else:
                        tenant_id = result
                except Exception:
                    pass
            
            # Start tracking
            ctx = CostTracker.start_context(tenant_id)
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Calculate cost
                duration = Decimal(time.time() - start_time)
                
                if model == "per-request":
                    CostTracker.record(
                        resource_type=resource_type,
                        quantity=Decimal(1),
                        unit="request",
                        resource_id=func.__name__,
                        duration_ms=float(duration * 1000)
                    )
                elif model == "per-second":
                    CostTracker.record(
                        resource_type=resource_type,
                        quantity=duration,
                        unit="seconds",
                        resource_id=func.__name__
                    )
                
                return result
                
            finally:
                await CostTracker.flush()
        
        return wrapper
    return decorator


class PricingService:
    """Service for retrieving pricing information"""
    
    # Default pricing (would be loaded from config)
    _pricing: Dict[ResourceType, Decimal] = {
        ResourceType.COMPUTE: Decimal("0.0001"),  # per second
        ResourceType.STORAGE: Decimal("0.10"),    # per GB
        ResourceType.NETWORK: Decimal("0.09"),    # per GB
        ResourceType.CACHE: Decimal("0.05"),      # per hour
        ResourceType.QUEUE: Decimal("0.01"),      # per 1M requests
        ResourceType.ML_INFERENCE: Decimal("0.02"),  # per 1K tokens
        ResourceType.THIRD_PARTY_API: Decimal("0.001"),  # per request
    }
    
    @classmethod
    def get_unit_cost(cls, resource_type: ResourceType, unit: str) -> Decimal:
        """Get cost per unit for resource type"""
        base_cost = cls._pricing.get(resource_type, Decimal("0"))
        
        # Adjust for unit
        unit_multipliers = {
            "request": Decimal("1"),
            "requests": Decimal("1"),
            "second": Decimal("1"),
            "seconds": Decimal("1"),
            "gb": Decimal("1"),
            "hour": Decimal("3600"),  # 3600 seconds
            "hours": Decimal("3600"),
            "token": Decimal("0.001"),
            "tokens": Decimal("0.001"),
        }
        
        return base_cost * unit_multipliers.get(unit.lower(), Decimal("1"))
    
    @classmethod
    def set_pricing(cls, resource_type: ResourceType, cost: Decimal) -> None:
        """Update pricing for resource type"""
        cls._pricing[resource_type] = cost


class CostEventStore:
    """Storage for cost events"""
    
    _events: List[CostEvent] = []
    
    @classmethod
    async def save_many(cls, events: List[CostEvent]) -> None:
        """Save multiple events"""
        cls._events.extend(events)
        
        # In production, would write to time-series DB
        # like InfluxDB, TimescaleDB, or cloud monitoring
    
    @classmethod
    def get_events(
        cls,
        tenant_id: Optional[str] = None,
        resource_type: Optional[ResourceType] = None,
        since: Optional[datetime] = None
    ) -> List[CostEvent]:
        """Query events"""
        events = cls._events
        
        if tenant_id:
            events = [e for e in events if e.tenant_id == tenant_id]
        
        if resource_type:
            events = [e for e in events if e.resource_type == resource_type]
        
        if since:
            events = [e for e in events if e.timestamp >= since]
        
        return events
    
    @classmethod
    def clear(cls) -> None:
        """Clear all events (for testing)"""
        cls._events.clear()


# Import asyncio for the decorator
import asyncio
