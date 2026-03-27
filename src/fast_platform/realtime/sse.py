"""
Server-Sent Events (SSE) support for FastMVC
"""

from typing import AsyncIterator, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import json
import asyncio


@dataclass
class SSEEvent:
    """Server-Sent Event"""
    data: str
    event: Optional[str] = None
    id: Optional[str] = None
    retry: Optional[int] = None
    comment: Optional[str] = None
    
    def to_string(self) -> str:
        """Convert to SSE format"""
        lines = []
        
        if self.comment:
            lines.append(f": {self.comment}")
        
        if self.event:
            lines.append(f"event: {self.event}")
        
        if self.id:
            lines.append(f"id: {self.id}")
        
        if self.retry:
            lines.append(f"retry: {self.retry}")
        
        # Data can be multi-line
        for line in self.data.split('\n'):
            lines.append(f"data: {line}")
        
        lines.append("\n")  # Empty line to end event
        return '\n'.join(lines)


class EventStream:
    """
    Server-Sent Event stream for async iteration
    """
    
    def __init__(
        self,
        heartbeat_interval: float = 30.0,
        retry_timeout: int = 3000
    ):
        self.heartbeat_interval = heartbeat_interval
        self.retry_timeout = retry_timeout
        self._queue: asyncio.Queue[SSEEvent] = asyncio.Queue()
        self._closed = False
        self._task: Optional[asyncio.Task] = None
    
    async def __aenter__(self):
        """Start heartbeat task"""
        self._task = asyncio.create_task(self._heartbeat())
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup"""
        self._closed = True
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _heartbeat(self):
        """Send periodic heartbeat comments"""
        while not self._closed:
            await asyncio.sleep(self.heartbeat_interval)
            if not self._closed:
                await self.send_comment("heartbeat")
    
    async def send(
        self,
        data: Any,
        event: Optional[str] = None,
        id: Optional[str] = None
    ) -> None:
        """Send an event"""
        if isinstance(data, dict):
            data = json.dumps(data)
        
        sse_event = SSEEvent(
            data=str(data),
            event=event,
            id=id
        )
        await self._queue.put(sse_event)
    
    async def send_json(self, data: dict, **kwargs) -> None:
        """Send JSON data"""
        await self.send(json.dumps(data), **kwargs)
    
    async def send_comment(self, comment: str) -> None:
        """Send a comment (ignored by client but keeps connection alive)"""
        sse_event = SSEEvent(data="", comment=comment)
        await self._queue.put(sse_event)
    
    async def __aiter__(self) -> AsyncIterator[str]:
        """Async iterator for SSE format"""
        # Send initial retry timeout
        yield f"retry: {self.retry_timeout}\n\n"
        
        while not self._closed:
            try:
                event = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=self.heartbeat_interval
                )
                yield event.to_string()
            except asyncio.TimeoutError:
                # Send heartbeat
                yield ": heartbeat\n\n"


def sse_endpoint(
    path: str,
    headers: Optional[Dict[str, str]] = None,
    ping_interval: float = 30.0
):
    """
    Decorator for SSE endpoints
    
    Args:
        path: Endpoint path
        headers: Additional headers
        ping_interval: Ping interval in seconds
    """
    def decorator(func):
        func._is_sse_endpoint = True
        func._sse_path = path
        func._sse_headers = headers or {}
        func._sse_ping_interval = ping_interval
        return func
    return decorator
