"""FastTasks Core Abstractions.

Defines the fundamental interfaces for background task processing,
execution strategies, and state management.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Union


class TaskStatus(str, Enum):
    """Lifecycle stages of a background job."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class TaskResult:
    """Outcome of a task execution cycle.
    
    Attributes:
        task_id (str): Reference to the job.
        status (TaskStatus): Final or current state.
        result (Any): Optional return value.
        error (Optional[str]): Exception details if failed.
        timestamp (datetime): When the result was generated.
    """
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class ITaskBackend(ABC):
    """Interface for task queuing and persistence engines.
    
    Backends are responsible for durable storage of task payloads and
    reliable distribution to workers.
    """

    @abstractmethod
    async def enqueue(
        self, 
        task_name: str, 
        args: tuple, 
        kwargs: dict, 
        task_id: Optional[str] = None,
        priority: int = 0,
        delay: Optional[int] = None
    ) -> str:
        """Add a job to the processing queue.
        
        Args:
            task_name (str): Fully qualified function path.
            args (tuple): Positional arguments.
            kwargs (dict): Named arguments.
            task_id (Optional[str]): Custom job ID.
            priority (int): Rank in the queue (higher = sooner).
            delay (Optional[int]): Postpone execution by seconds.
            
        Returns:
            str: Task tracking ID.
        """
        pass

    @abstractmethod
    async def dequeue(self, timeout: Optional[int] = None) -> Optional[dict]:
        """Fetch the next available job for processing.
        
        Args:
            timeout (Optional[int]): Seconds to block before returning None.
            
        Returns:
            Optional[dict]: Task payload or None.
        """
        pass

    @abstractmethod
    async def get_result(self, task_id: str) -> Optional[TaskResult]:
        """Retrieve the execution state of a specific job.
        
        Args:
            task_id (str): The job identifier.
            
        Returns:
            Optional[TaskResult]: Stored result if available.
        """
        pass

    @abstractmethod
    async def set_result(self, result: TaskResult) -> bool:
        """Store the outcome of a job execution.
        
        Args:
            result (TaskResult): The outcome payload.
            
        Returns:
            bool: Storage success status.
        """
        pass
