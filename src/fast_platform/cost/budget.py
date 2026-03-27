"""
Budget Management for Cost Tracking
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal


@dataclass
class BudgetAlert:
    """Budget alert configuration"""
    threshold_percent: float
    action: str  # "notify", "throttle", "block"
    channels: List[str] = field(default_factory=list)
    recipients: Optional[List[str]] = None
    
    @classmethod
    def at(
        cls,
        percent: float,
        notify: str = "slack",
        action: str = "notify"
    ) -> "BudgetAlert":
        """Convenience factory"""
        return cls(
            threshold_percent=percent,
            action=action,
            channels=[notify]
        )


@dataclass
class Budget:
    """Budget for cost control"""
    id: str
    name: str
    tenant_id: Optional[str]
    monthly_limit: Decimal
    alert_thresholds: List[BudgetAlert] = field(default_factory=list)
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    current_spend: Decimal = Decimal("0")
    projected_spend: Decimal = Decimal("0")
    on_exceed: str = "notify"
    
    def get_spend_percentage(self) -> float:
        """Get current spend as percentage of limit"""
        if self.monthly_limit == 0:
            return 0.0
        return float(self.current_spend / self.monthly_limit * 100)
    
    def is_exceeded(self) -> bool:
        """Check if budget is exceeded"""
        return self.current_spend >= self.monthly_limit
    
    async def check_and_alert(self) -> List[BudgetAlert]:
        """Check budget and trigger alerts"""
        triggered = []
        spend_percent = self.get_spend_percentage()
        
        for alert in self.alert_thresholds:
            if spend_percent >= alert.threshold_percent:
                triggered.append(alert)
                await self._trigger_alert(alert, spend_percent)
        
        return triggered
    
    async def _trigger_alert(self, alert: BudgetAlert, spend_percent: float) -> None:
        """Send alert through configured channels"""
        message = (
            f"🚨 Budget Alert: {self.name}\n"
            f"Current spend: ${self.current_spend:.2f} ({spend_percent:.1f}% of limit)\n"
            f"Monthly limit: ${self.monthly_limit:.2f}"
        )
        
        # Log the alert
        print(f"[ALERT] {message}")
        
        # Execute action
        if alert.action == "throttle":
            await CostThrottler.enable_throttling(self.tenant_id)
        elif alert.action == "block":
            await CostThrottler.block_tenant(self.tenant_id)


class BudgetManager:
    """Manage budgets across tenants"""
    
    _budgets: Dict[str, Budget] = {}
    
    @classmethod
    async def create_budget(cls, budget: Budget) -> Budget:
        """Create a new budget"""
        cls._budgets[budget.id] = budget
        return budget
    
    @classmethod
    async def update_spend(
        cls,
        tenant_id: Optional[str],
        amount: Decimal
    ) -> None:
        """Update spend for a budget"""
        budget = cls._get_budget_for_tenant(tenant_id)
        if budget:
            budget.current_spend += amount
            await budget.check_and_alert()
    
    @classmethod
    def get_budget(cls, budget_id: str) -> Optional[Budget]:
        """Get budget by ID"""
        return cls._budgets.get(budget_id)
    
    @classmethod
    def get_budget_for_tenant(cls, tenant_id: str) -> Optional[Budget]:
        """Get budget for tenant"""
        return cls._get_budget_for_tenant(tenant_id)
    
    @classmethod
    def _get_budget_for_tenant(
        cls,
        tenant_id: Optional[str]
    ) -> Optional[Budget]:
        """Get budget for tenant or global budget"""
        if tenant_id:
            # Find tenant-specific budget
            for budget in cls._budgets.values():
                if budget.tenant_id == tenant_id:
                    return budget
        
        # Return global budget
        for budget in cls._budgets.values():
            if budget.tenant_id is None:
                return budget
        
        return None
    
    @classmethod
    def list_budgets(cls) -> List[Budget]:
        """List all budgets"""
        return list(cls._budgets.values())
    
    @classmethod
    def clear(cls) -> None:
        """Clear all budgets"""
        cls._budgets.clear()


class CostThrottler:
    """Throttling based on budget limits"""
    
    _throttled_tenants: set = set()
    _blocked_tenants: set = set()
    
    @classmethod
    async def enable_throttling(cls, tenant_id: Optional[str]) -> None:
        """Enable throttling for tenant"""
        if tenant_id:
            cls._throttled_tenants.add(tenant_id)
            print(f"[THROTTLE] Enabled throttling for tenant: {tenant_id}")
    
    @classmethod
    async def disable_throttling(cls, tenant_id: Optional[str]) -> None:
        """Disable throttling for tenant"""
        if tenant_id:
            cls._throttled_tenants.discard(tenant_id)
    
    @classmethod
    async def block_tenant(cls, tenant_id: Optional[str]) -> None:
        """Block tenant completely"""
        if tenant_id:
            cls._blocked_tenants.add(tenant_id)
            print(f"[BLOCK] Blocked tenant: {tenant_id}")
    
    @classmethod
    async def unblock_tenant(cls, tenant_id: Optional[str]) -> None:
        """Unblock tenant"""
        if tenant_id:
            cls._blocked_tenants.discard(tenant_id)
    
    @classmethod
    def is_throttled(cls, tenant_id: Optional[str]) -> bool:
        """Check if tenant is throttled"""
        return tenant_id in cls._throttled_tenants
    
    @classmethod
    def is_blocked(cls, tenant_id: Optional[str]) -> bool:
        """Check if tenant is blocked"""
        return tenant_id in cls._blocked_tenants
    
    @classmethod
    def check_access(cls, tenant_id: Optional[str]) -> bool:
        """Check if tenant has access"""
        return not cls.is_blocked(tenant_id)
