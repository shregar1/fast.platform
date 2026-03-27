"""FastTasks Task Decorator.

A high-level interface for declaring background tasks with 
built-in retry logic, scheduling, and ecosystem integration.
"""

import asyncio
import functools
import uuid
import inspect
from typing import Any, Callable, List, Optional, TypeVar, Union, cast

from ..core.base import ITaskBackend, TaskStatus, TaskResult
from ..core.registry import TaskRegistry, TaskMetadata

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])


class TaskManager:
    """Singleton task manager for FastTasks.
    
    Handles global backend association and provide primary 
    queuing APIs for the FastPlatform ecosystem.
    """

    _instance = None
    _backend: Optional[ITaskBackend] = None

    def __new__(cls):
        """Standard singleton implementation."""
        if cls._instance is None:
            cls._instance = super(TaskManager, cls).__new__(cls)
        return cls._instance

    @property
    def backend(self) -> ITaskBackend:
        """Get the current task storage engine.
        
        Returns:
            ITaskBackend: The active engine.
        """
        if self._backend is None:
            # Lazy import to avoid circular dependencies
            from ..backends.memory import InMemoryTaskBackend
            self._backend = InMemoryTaskBackend()
        return self._backend

    @backend.setter
    def backend(self, value: ITaskBackend):
        """Switch the task engine at runtime.
        
        Args:
            value (ITaskBackend): New engine instance.
        """
        self._backend = value

    async def enqueue(
        self, 
        task_name: str, 
        *args, 
        **kwargs
    ) -> str:
        """Low-level queueing API.
        
        Args:
            task_name (str): Identifier.
            args/kwargs: Execution data.
            
        Returns:
            str: Tracking ID.
        """
        return await self.backend.enqueue(task_name, args, kwargs)


# Singleton instance
fast_tasks = TaskManager()


def task(
    name: Optional[str] = None,
    retry: int = 0,
    retry_delay: int = 5,
    backoff: float = 2.0,
    priority: int = 0
):
    """Declare a function as a background task.
    
    Args:
        name (Optional[str]): Override identifier (Full name used if None).
        retry (int): Attempts beyond first execution.
        retry_delay (int): Seconds between attempts.
        backoff (float): Growth factor (exponential).
        priority (int): Dispatch rank.
        
    Returns:
        Callable: The original function with a `.delay()` helper added.
    """
    def decorator(fn: F) -> F:
        task_name = name or f"{fn.__module__}.{fn.__qualname__}"
        
        # Register task definition
        metadata = TaskMetadata(
            fn=fn,
            name=task_name,
            retry=retry,
            retry_delay=retry_delay,
            backoff=backoff
        )
        TaskRegistry.register(metadata)

        @functools.wraps(fn)
        async def delay(*args, **kwargs) -> str:
            """Queues the task for background execution.
            
            Returns:
                str: Task tracking ID.
            """
            return await fast_tasks.backend.enqueue(
                task_name, 
                args, 
                kwargs,
                priority=priority
            )

        # Inject .delay() helper onto original function
        setattr(fn, "delay", delay)
        return fn

    return decorator
