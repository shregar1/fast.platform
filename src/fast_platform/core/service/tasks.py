"""FastPlatform Tasks Service.

Unified background processing interface for the FastPlatform ecosystem,
enabling reliable task delegation and lifecycle monitoring.
"""

from typing import Any, Callable, Dict, Optional, TypeVar
from ...core.service.abstraction import IService

from ...task import task as fast_task, fast_tasks

T = TypeVar("T")


class TasksPlatformService(IService):
    """Platform-level task orchestration service.
    
    Provides a high-level abstraction for enqueuing jobs and checking
    execution results, ensuring loose coupling between domain logic and
    the underlying processing engine.
    """

    def __init__(self, backend_override: Optional[Any] = None):
        """Initialize with optional backend configuration."""
        if fast_tasks and backend_override:
            fast_tasks.backend = backend_override

    async def enqueue(self, task_name: str, *args, **kwargs) -> str:
        """Hand off a job to the background worker.
        
        Args:
            task_name (str): The registered task identifier.
            args/kwargs: Execution payload.
            
        Returns:
            str: Tracking ID.
        """
        if not fast_tasks:
            raise RuntimeError("FastTasks engine not available")
        return await fast_tasks.enqueue(task_name, *args, **kwargs)

    async def get_status(self, task_id: str) -> Optional[str]:
        """Check the residency and state of a job.
        
        Args:
            task_id (str): Reference.
            
        Returns:
            Optional[str]: Status string or None if unknown.
        """
        if not fast_tasks:
            return None
        result = await fast_tasks.backend.get_result(task_id)
        return result.status if result else None
