"""FastTasks In-Memory Backend Implementation.

Provides a volatile, high-performance task queuing engine using 
asyncio.PriorityQueue for local-only development and low-latency task processing.
"""

import asyncio
import uuid
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ..core.base import ITaskBackend, TaskStatus, TaskResult


class InMemoryTaskBackend(ITaskBackend):
    """Local volatile task store using asyncio.PriorityQueue.
    
    Suitable for development environments or small-scale applications
    where persistence is not critical.
    """

    def __init__(self):
        """Initialize internal state structures."""
        self._queue = asyncio.PriorityQueue()
        self._results: Dict[str, TaskResult] = {}
        self._lock = asyncio.Lock()

    async def enqueue(
        self, 
        task_name: str, 
        args: tuple, 
        kwargs: dict, 
        task_id: Optional[str] = None,
        priority: int = 0,
        delay: Optional[int] = None
    ) -> str:
        """Add a job to the local queue.
        
        Args:
            task_name (str): Label.
            args/kwargs: Data.
            task_id/priority/delay: Metadata.
            
        Returns:
            str: Tracking identifier.
        """
        tid = task_id or str(uuid.uuid4())
        payload = {
            "task_id": tid,
            "task_name": task_name,
            "args": args,
            "kwargs": kwargs,
            "priority": priority,
            "enqueue_time": time.time(),
            "target_time": time.time() + (delay or 0)
        }
        
        # PriorityQueue pops lowest first
        await self._queue.put((priority, payload))
        
        async with self._lock:
            self._results[tid] = TaskResult(
                task_id=tid, 
                status=TaskStatus.PENDING,
                timestamp=datetime.now()
            )
            
        return tid

    async def dequeue(self, timeout: Optional[int] = None) -> Optional[dict]:
        """Pop and validate the head job.
        
        Returns:
            Optional[dict]: Job data or None if time not reached.
        """
        try:
            # wait_for with timeout on the queue fetch
            priority, payload = await asyncio.wait_for(
                self._queue.get(), 
                timeout=timeout or 5
            )
            
            now = time.time()
            wait_rem = payload["target_time"] - now
            if wait_rem > 0:
                # Still too early - Put it back
                await self._queue.put((priority, payload))
                await asyncio.sleep(min(0.5, wait_rem))
                return None
                
            return payload
        except (asyncio.TimeoutError, asyncio.QueueEmpty):
            return None

    async def get_result(self, task_id: str) -> Optional[TaskResult]:
        """Fetch result from local memory store."""
        async with self._lock:
            return self._results.get(task_id)

    async def set_result(self, result: TaskResult) -> bool:
        """Record outcome in local memory."""
        async with self._lock:
            self._results[result.task_id] = result
        return True
