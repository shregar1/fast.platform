"""FastTasks Task Registry.

Unified storage and lookup for job metadata, enabling discovery and 
dispatching by name throughout the worker lifecycle.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional


@dataclass
class TaskMetadata:
    """Description of a registered background operation.
    
    Attributes:
        fn (Callable): The actual function to execute.
        name (str): Unique identifier (FQDN by default).
        retry (int): Max failure count before giving up.
        retry_delay (int): Base interval between attempts (seconds).
        backoff (float): Growth factor for consecutive retries.
    """
    fn: Callable
    name: str
    retry: int = 0
    retry_delay: int = 5
    backoff: float = 2.0


class TaskRegistry:
    """Internal singleton for managing task definitions.
    
    Ensures that workers can resolve function names passed in 
    queue messages back to executable code.
    """

    _tasks: Dict[str, TaskMetadata] = {}

    @classmethod
    def register(cls, metadata: TaskMetadata) -> None:
        """Add a task definition to the registry.
        
        Args:
            metadata (TaskMetadata): Definition payload.
        """
        cls._tasks[metadata.name] = metadata

    @classmethod
    def get(cls, name: str) -> Optional[TaskMetadata]:
        """Fetch metadata for a given task.
        
        Args:
            name (str): Identifier.
            
        Returns:
            Optional[TaskMetadata]: Metadata or None.
        """
        return cls._tasks.get(name)

    @classmethod
    def all_tasks(cls) -> Dict[str, TaskMetadata]:
        """Return every registered task definition."""
        return cls._tasks.copy()
