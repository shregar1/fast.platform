"""FastTasks Redis Backend Implementation.

Provides a distributed, persistent task queuing engine using Redis
Lists for reliable message delivery and Hashes for result persistence.
"""

import json
import pickle
import uuid
import time
from typing import Any, Dict, List, Optional, Tuple

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

from ..core.base import ITaskBackend, TaskStatus, TaskResult


class RedisTaskBackend(ITaskBackend):
    """Reliable Redis-backed task queueing storage.
    
    Implements a safe-worker pattern using RPOPLPUSH to ensure no jobs
    are lost during crashes. Supports TTL on result storage.
    """

    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 6379, 
        db: int = 0, 
        password: Optional[str] = None,
        key_prefix: str = "fasttasks:"
    ):
        """Initialize Redis parameters.
        
        Args:
            host (str): Redis host.
            port (int): Redis port.
            db (int): Database index.
            password (Optional[str]): Password.
            key_prefix (str): Prefix to isolate queues.
        """
        if redis is None:
            raise ImportError("redis-py package is required for RedisTaskBackend. Install with 'pip install redis'")
            
        self._client = redis.Redis(
            host=host, 
            port=port, 
            db=db, 
            password=password, 
            decode_responses=False
        )
        self._prefix = key_prefix
        self._queue_key = f"{key_prefix}queue:default"
        self._processing_key = f"{key_prefix}processing:worker"
        self._result_key = f"{key_prefix}results"

    def _get_result_path(self, task_id: str) -> str:
        """Full path for result storage."""
        return f"{self._result_key}:{task_id}"

    async def enqueue(
        self, 
        task_name: str, 
        args: tuple, 
        kwargs: dict, 
        task_id: Optional[str] = None,
        priority: int = 0,
        delay: Optional[int] = None
    ) -> str:
        """Push a serialized job onto the Redis list.
        
        Args:
            task_name (str): Label.
            args/kwargs: Data.
            task_id (Optional[str]): Identifier.
            priority (int): Dispatch rank.
            delay (Optional[int]): Postpone.
            
        Returns:
            str: Task tracker.
        """
        tid = task_id or str(uuid.uuid4())
        payload = {
            "task_id": tid,
            "task_name": task_name,
            "args": args,
            "kwargs": kwargs,
            "priority": priority,
            "target_time": time.time() + (delay or 0)
        }
        
        # Serialize with pickle for complex object support
        data = pickle.dumps(payload)
        
        # LPUSH for FIFO (with RPOP on worker)
        await self._client.lpush(self._queue_key, data)
        
        # Initial status
        await self.set_result(TaskResult(task_id=tid, status=TaskStatus.PENDING))
        return tid

    async def dequeue(self, timeout: Optional[int] = None) -> Optional[dict]:
        """Atomically pop a task into the processing queue.
        
        Args:
            timeout (Optional[int]): Block duration.
            
        Returns:
            Optional[dict]: Next job or None.
        """
        # Note: RPOPLPUSH is being deprecated in favor of LMOVE,
        # but for compatibility, we use BRPOPLPUSH (blocking variant).
        data = await self._client.brpoplpush(
            self._queue_key, 
            self._processing_key, 
            timeout=timeout or 5
        )
        
        if data:
            payload = pickle.loads(data)
            
            # Scheduling check
            if payload["target_time"] > time.time():
                # Still too early - Put back onto queue
                await self._client.lrem(self._processing_key, 1, data)
                await self._client.lpush(self._queue_key, data)
                return None
            
            return payload
        return None

    async def get_result(self, task_id: str) -> Optional[TaskResult]:
        """Retrieve outcome from the result hash.
        
        Args:
            task_id (str): Reference.
            
        Returns:
            Optional[TaskResult]: Result data.
        """
        data = await self._client.get(self._get_result_path(task_id))
        if data:
            return pickle.loads(data)
        return None

    async def set_result(self, result: TaskResult) -> bool:
        """Persist result with optional TTL (24h default).
        
        Args:
            result (TaskResult): Outcome payload.
            
        Returns:
            bool: Insertion status.
        """
        path = self._get_result_path(result.task_id)
        data = pickle.dumps(result)
        
        # Auto-expire results after 24 hours to prevent memory bloat
        await self._client.setex(path, 86400, data)
        return True
