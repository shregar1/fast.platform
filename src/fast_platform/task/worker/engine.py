"""FastTasks Worker Engine.

A multi-tasking, event-driven worker core designed for high-throughput
background job processing with resilient error handling and status monitoring.
"""

import asyncio
import logging
import time
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.base import ITaskBackend, TaskStatus, TaskResult
from ..core.registry import TaskRegistry, TaskMetadata
from ..decorators import fast_tasks

logger = logging.getLogger("fast_tasks.worker")


class Worker:
    """Core execution engine for FastTasks.
    
    Responsible for polling the backend, launching task coroutines,
    and managing job lifecycles across successful and failed states.
    """

    def __init__(
        self, 
        concurrency: int = 10,
        poll_interval: float = 0.5,
        backend: Optional[ITaskBackend] = None
    ):
        """Initialize worker configuration.
        
        Args:
            concurrency (int): Maximum active tasks.
            poll_interval (float): Seconds between queue checks.
            backend (Optional[ITaskBackend]): Override default engine.
        """
        self._concurrency = concurrency
        self._poll_interval = poll_interval
        self._backend = backend or fast_tasks.backend
        self._active_tasks: List[asyncio.Task] = []
        self._running = False

    async def start(self) -> None:
        """Launch the worker loop in the current thread."""
        self._running = True
        logger.info(f"FastTasks Worker started (concurrency={self._concurrency})")
        
        while self._running:
            # Cleanup finished tasks
            self._active_tasks = [t for t in self._active_tasks if not t.done()]
            
            if len(self._active_tasks) < self._concurrency:
                payload = await self._backend.dequeue(timeout=1)
                if payload:
                    task_id = payload["task_id"]
                    logger.debug(f"Picked up job: {task_id}")
                    
                    # Spawn task processing coroutine
                    worker_task = asyncio.create_task(self._process_task(payload))
                    self._active_tasks.append(worker_task)
                else:
                    # Brief rest if queue is dry
                    await asyncio.sleep(self._poll_interval)
            else:
                # Max concurrency reached, wait until at least one task finishes
                await asyncio.sleep(0.1)

    async def stop(self) -> None:
        """Initiate graceful shutdown."""
        self._running = False
        if self._active_tasks:
            logger.info(f"Waiting for {len(self._active_tasks)} active tasks...")
            await asyncio.gather(*self._active_tasks, return_exceptions=True)
        logger.info("FastTasks Worker stopped.")

    async def _process_task(self, payload: dict) -> None:
        """Internal execution lifecycle for a single job.
        
        Args:
            payload (dict): Data from the backend.
        """
        task_id = payload["task_id"]
        task_name = payload["task_name"]
        args = payload["args"]
        kwargs = payload["kwargs"]
        
        # Track attempts
        metadata = TaskRegistry.get(task_name)
        if not metadata:
            logger.error(f"Failed to find metadata for task: {task_name}")
            return

        # Mark as RUNNING
        await self._backend.set_result(TaskResult(task_id=task_id, status=TaskStatus.RUNNING))
        
        # Execute with retry logic
        attempts = 0
        total_attempts = metadata.retry + 1
        
        while attempts < total_attempts:
            try:
                # Update status for retries
                if attempts > 0:
                    await self._backend.set_result(
                        TaskResult(task_id=task_id, status=TaskStatus.RETRYING)
                    )
                    
                # Handle both async and sync functions transparently
                if asyncio.iscoroutinefunction(metadata.fn):
                    result_value = await metadata.fn(*args, **kwargs)
                else:
                    # Use threadpool for sync blocking functions
                    loop = asyncio.get_running_loop()
                    result_value = await loop.run_in_executor(None, metadata.fn, *args, **kwargs)
                
                # Report Success
                await self._backend.set_result(
                    TaskResult(
                        task_id=task_id, 
                        status=TaskStatus.SUCCESS, 
                        result=result_value
                    )
                )
                logger.debug(f"Job {task_id} completed successfully.")
                return
                
            except Exception as e:
                attempts += 1
                error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
                
                if attempts < total_attempts:
                    # Log and backoff
                    wait_time = metadata.retry_delay * (metadata.backoff ** (attempts - 1))
                    logger.warning(
                        f"Job {task_id} failed (attempt {attempts}). "
                        f"Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    # Exhausted!
                    logger.error(f"Job {id} failed definitively after {attempts} attempts.")
                    await self._backend.set_result(
                        TaskResult(
                            task_id=task_id, 
                            status=TaskStatus.FAILED, 
                            error=error_msg
                        )
                    )
