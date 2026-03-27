"""FastTasks Background Processing Ecosystem.

A distributed, persistent task queuing engine for FastMVC applications, 
providing high-level abstractions over in-memory and Redis backends 
with robust retry-logic, workers, and monitoring interfaces.
"""

from .core.base import ITaskBackend, TaskStatus, TaskResult
from .core.registry import TaskRegistry, TaskMetadata
from .backends.memory import InMemoryTaskBackend
from .backends.redis import RedisTaskBackend
from .decorators import TaskManager, task, fast_tasks
from .worker.engine import Worker


__all__ = [
    "ITaskBackend",
    "TaskStatus",
    "TaskResult",
    "TaskRegistry",
    "TaskMetadata",
    "InMemoryTaskBackend",
    "RedisTaskBackend",
    "TaskManager",
    "task",
    "fast_tasks",
    "Worker",
]

# Version management
__version__ = "1.0.0"
