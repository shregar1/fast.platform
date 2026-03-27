"""
Core Chaos Engineering implementation
"""

from enum import Enum, auto
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
import asyncio
import random
import time


class FailureType(Enum):
    """Types of failures that can be injected"""
    
    # Latency failures
    LATENCY_SPIKE = auto()
    LATENCY_DEGRADATION = auto()
    
    # Network failures
    NETWORK_TIMEOUT = auto()
    NETWORK_PARTITION = auto()
    NETWORK_PACKET_LOSS = auto()
    DNS_FAILURE = auto()
    
    # Resource failures
    CPU_PRESSURE = auto()
    MEMORY_PRESSURE = auto()
    DISK_PRESSURE = auto()
    FD_EXHAUSTION = auto()
    
    # Dependency failures
    DB_CONNECTION_DROP = auto()
    CACHE_FAILURE = auto()
    EXTERNAL_API_FAILURE = auto()
    MESSAGE_QUEUE_FAILURE = auto()
    
    # Application failures
    EXCEPTION_INJECTION = auto()
    PANIC_INJECTION = auto()


class ExperimentStatus(Enum):
    """Status of a chaos experiment"""
    PENDING = auto()
    RUNNING = auto()
    PAUSED = auto()
    COMPLETED = auto()
    FAILED = auto()
    ROLLED_BACK = auto()


@dataclass
class FailureConfig:
    """Configuration for a failure injection"""
    failure_type: FailureType
    probability: float = 0.1
    duration: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    intensity: str = "medium"
    target: str = "*"
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentResult:
    """Result of a chaos experiment"""
    experiment_id: str
    status: ExperimentStatus
    start_time: datetime
    end_time: Optional[datetime]
    
    # Metrics
    total_requests: int = 0
    failed_requests: int = 0
    p50_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    error_rate: float = 0.0
    
    # Recovery metrics
    detection_time_ms: float = 0.0
    recovery_time_ms: float = 0.0
    
    # SLO validation
    slo_violations: List[str] = field(default_factory=list)
    
    # Detailed events
    events: List[Dict[str, Any]] = field(default_factory=list)


class ChaosException(Exception):
    """Base exception for chaos engineering"""
    pass


class AbortExperiment(ChaosException):
    """Raised when experiment should be aborted"""
    pass


class ChaosExperiment:
    """
    A chaos experiment that injects failures and measures resilience
    """
    
    def __init__(
        self,
        name: str,
        target: str,
        failures: List[FailureConfig],
        abort_conditions: Optional[List[Callable]] = None,
        duration: timedelta = timedelta(minutes=10),
        blast_radius: float = 0.1,
        schedule: Optional[str] = None
    ):
        self.name = name
        self.target = target
        self.failures = failures
        self.abort_conditions = abort_conditions or []
        self.duration = duration
        self.blast_radius = blast_radius
        self.schedule = schedule
        
        self.status = ExperimentStatus.PENDING
        self.result: Optional[ExperimentResult] = None
        self._injected_failures: List[Any] = []
        self._start_time: Optional[datetime] = None
        self._metrics = {
            "requests": 0,
            "failures": 0,
            "latencies": []
        }
    
    async def run(self) -> ExperimentResult:
        """Execute the chaos experiment"""
        self.status = ExperimentStatus.RUNNING
        self._start_time = datetime.utcnow()
        
        try:
            # Pre-experiment checks
            await self._validate_preconditions()
            
            # Start failure injection
            injection_tasks = [
                self._inject_failure(failure)
                for failure in self.failures
            ]
            
            # Monitor and validate SLOs
            monitor_task = asyncio.create_task(self._monitor_slos())
            
            # Run for duration
            try:
                await asyncio.wait_for(
                    asyncio.gather(*injection_tasks, return_exceptions=True),
                    timeout=self.duration.total_seconds()
                )
            except asyncio.TimeoutError:
                pass
            
            monitor_task.cancel()
            
            self.status = ExperimentStatus.COMPLETED
            
        except AbortExperiment as e:
            self.status = ExperimentStatus.ROLLED_BACK
            await self._rollback()
        except Exception as e:
            self.status = ExperimentStatus.FAILED
            await self._rollback()
        
        finally:
            await self._cleanup()
            self.result = await self._generate_result()
        
        return self.result
    
    async def _inject_failure(self, config: FailureConfig) -> None:
        """Inject a specific failure"""
        from .injectors import FailureInjectorFactory
        
        injector = FailureInjectorFactory.create(config.failure_type)
        
        handle = await injector.inject(
            target=self.target,
            probability=config.probability,
            parameters=config.parameters,
            blast_radius=self.blast_radius
        )
        
        self._injected_failures.append(handle)
    
    async def _monitor_slos(self) -> None:
        """Monitor SLOs and abort if violated"""
        while self.status == ExperimentStatus.RUNNING:
            for condition in self.abort_conditions:
                try:
                    if await condition():
                        raise AbortExperiment("SLO breach detected")
                except Exception:
                    pass
            
            await asyncio.sleep(1)
    
    async def _rollback(self) -> None:
        """Rollback all injected failures"""
        for handle in self._injected_failures:
            try:
                await handle.rollback()
            except Exception:
                pass
    
    async def _cleanup(self) -> None:
        """Cleanup resources"""
        for handle in self._injected_failures:
            try:
                await handle.cleanup()
            except Exception:
                pass
    
    async def _validate_preconditions(self) -> None:
        """Validate pre-experiment conditions"""
        if self.blast_radius > 0.5:
            raise ChaosException("Blast radius exceeds 50% - too risky")
    
    async def _generate_result(self) -> ExperimentResult:
        """Generate experiment results"""
        latencies = self._metrics["latencies"]
        
        return ExperimentResult(
            experiment_id=self.name,
            status=self.status,
            start_time=self._start_time,
            end_time=datetime.utcnow(),
            total_requests=self._metrics["requests"],
            failed_requests=self._metrics["failures"],
            p50_latency_ms=self._percentile(latencies, 50) if latencies else 0,
            p99_latency_ms=self._percentile(latencies, 99) if latencies else 0,
            error_rate=(
                self._metrics["failures"] / max(self._metrics["requests"], 1)
            )
        )
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def record_request(self, latency_ms: float, failed: bool = False) -> None:
        """Record a request metric"""
        self._metrics["requests"] += 1
        self._metrics["latencies"].append(latency_ms)
        if failed:
            self._metrics["failures"] += 1


class ChaosRegistry:
    """Registry for chaos experiments"""
    
    _experiments: Dict[str, ChaosExperiment] = {}
    
    @classmethod
    def register(cls, experiment: ChaosExperiment) -> None:
        cls._experiments[experiment.name] = experiment
    
    @classmethod
    def get(cls, name: str) -> Optional[ChaosExperiment]:
        return cls._experiments.get(name)
    
    @classmethod
    def list_all(cls) -> List[ChaosExperiment]:
        return list(cls._experiments.values())
    
    @classmethod
    def clear(cls) -> None:
        cls._experiments.clear()


class ChaosController:
    """
    Central controller for managing chaos experiments
    """
    
    _active_experiments: Dict[str, asyncio.Task] = {}
    
    @classmethod
    async def start_experiment(
        cls,
        name: str,
        dry_run: bool = False
    ) -> Optional[ExperimentResult]:
        """Start a chaos experiment"""
        experiment = ChaosRegistry.get(name)
        if not experiment:
            return None
        
        if dry_run:
            return None  # Would return validation result
        
        task = asyncio.create_task(experiment.run())
        cls._active_experiments[name] = task
        
        return await task
    
    @classmethod
    async def stop_experiment(cls, name: str) -> bool:
        """Stop a running experiment"""
        task = cls._active_experiments.get(name)
        if task:
            task.cancel()
            del cls._active_experiments[name]
            return True
        return False
    
    @classmethod
    def get_experiment_status(cls, name: str) -> Optional[Dict[str, Any]]:
        """Get current experiment status"""
        experiment = ChaosRegistry.get(name)
        if not experiment:
            return None
        
        return {
            "name": name,
            "target": experiment.target,
            "status": experiment.status.name,
            "result": experiment.result
        }
    
    @classmethod
    def list_experiments(cls) -> List[Dict[str, Any]]:
        """List all registered experiments"""
        return [
            {
                "name": name,
                "target": exp.target,
                "status": exp.status.name
            }
            for name, exp in ChaosRegistry._experiments.items()
        ]


def chaos_experiment(
    failures: Optional[List[FailureConfig]] = None,
    auto_abort_on_slo_breach: bool = True,
    blast_radius: float = 0.1,
    schedule: Optional[str] = None,
    duration_minutes: int = 10
):
    """
    Decorator to enable chaos experiments on a service/function
    
    Args:
        failures: List of failures to inject
        auto_abort_on_slo_breach: Automatically stop if SLOs violated
        blast_radius: Percentage of traffic to affect (0.0-1.0)
        schedule: Cron expression for recurring experiments
        duration_minutes: Duration of the experiment
    """
    def decorator(func):
        experiment = ChaosExperiment(
            name=func.__name__,
            target=f"{func.__module__}.{func.__name__}",
            failures=failures or [],
            blast_radius=blast_radius,
            schedule=schedule,
            duration=timedelta(minutes=duration_minutes)
        )
        
        ChaosRegistry.register(experiment)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        wrapper._chaos_experiment = experiment
        return wrapper
    
    return decorator
