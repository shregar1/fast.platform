"""
SLA (Service Level Agreement) tracking
"""

from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
import time


class SLAType(Enum):
    """Types of SLAs"""
    AVAILABILITY = "availability"  # % uptime
    LATENCY = "latency"            # Response time
    ERROR_RATE = "error_rate"      # Error percentage
    THROUGHPUT = "throughput"      # Requests per second


@dataclass
class SLAMetric:
    """SLA metric measurement"""
    value: float
    timestamp: datetime
    target: float
    met: bool


class SLA:
    """
    Service Level Agreement tracker
    """
    
    def __init__(
        self,
        name: str,
        sla_type: SLAType,
        target: float,
        window: str = "30d",
        alert_threshold: Optional[float] = None
    ):
        self.name = name
        self.sla_type = sla_type
        self.target = target
        self.window = self._parse_window(window)
        self.alert_threshold = alert_threshold or (target * 0.99)
        self._measurements: list = []
    
    def _parse_window(self, window: str) -> int:
        """Parse window string to seconds"""
        units = {"h": 3600, "d": 86400, "w": 604800}
        
        for unit, seconds in units.items():
            if window.endswith(unit):
                return int(window[:-1]) * seconds
        
        return int(window)
    
    def record(self, value: float) -> SLAMetric:
        """Record a measurement"""
        met = value >= self.target
        
        if self.sla_type == SLAType.ERROR_RATE:
            met = value <= self.target
        
        metric = SLAMetric(
            value=value,
            timestamp=datetime.utcnow(),
            target=self.target,
            met=met
        )
        
        self._measurements.append(metric)
        self._cleanup_old()
        
        return metric
    
    def _cleanup_old(self) -> None:
        """Remove old measurements"""
        cutoff = datetime.utcnow().timestamp() - self.window
        self._measurements = [
            m for m in self._measurements
            if m.timestamp.timestamp() > cutoff
        ]
    
    def get_current_sla(self) -> float:
        """Calculate current SLA percentage"""
        if not self._measurements:
            return 100.0
        
        met_count = sum(1 for m in self._measurements if m.met)
        return (met_count / len(self._measurements)) * 100
    
    def is_breached(self) -> bool:
        """Check if SLA is currently breached"""
        return self.get_current_sla() < self.alert_threshold
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get SLA metrics"""
        current = self.get_current_sla()
        
        return {
            "name": self.name,
            "type": self.sla_type.value,
            "target": self.target,
            "current": current,
            "breached": current < self.alert_threshold,
            "measurements_count": len(self._measurements),
            "window_seconds": self.window
        }


def track_sla(
    name: str,
    sla_type: SLAType = SLAType.LATENCY,
    target: float = 99.9,
    window: str = "30d"
):
    """
    Decorator to track SLA for a function
    
    Args:
        name: SLA name
        sla_type: Type of SLA
        target: Target value
        window: Measurement window
    """
    sla = SLA(name, sla_type, target, window)
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                if sla_type == SLAType.LATENCY:
                    elapsed = (time.time() - start) * 1000  # ms
                    sla.record(elapsed)
                elif sla_type == SLAType.AVAILABILITY:
                    sla.record(100.0)
                
                return result
                
            except Exception:
                if sla_type == SLAType.AVAILABILITY:
                    sla.record(0.0)
                elif sla_type == SLAType.ERROR_RATE:
                    sla.record(100.0)
                raise
        
        wrapper._sla = sla
        return wrapper
    
    return decorator
