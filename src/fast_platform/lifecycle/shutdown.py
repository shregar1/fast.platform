"""
Graceful shutdown management
"""

from typing import List, Callable, Awaitable, Optional
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ShutdownHook:
    """A shutdown hook"""
    name: str
    handler: Callable[[], Awaitable[None]]
    priority: int = 0  # Higher = executed first
    timeout: float = 30.0


@dataclass
class StartupHook:
    """A startup hook"""
    name: str
    handler: Callable[[], Awaitable[None]]
    priority: int = 0  # Higher = executed first
    timeout: float = 30.0


class ShutdownManager:
    """
    Manages graceful shutdown procedures
    """
    
    _hooks: List[ShutdownHook] = []
    _is_shutting_down = False
    
    @classmethod
    def register(
        cls,
        handler: Callable[[], Awaitable[None]],
        name: Optional[str] = None,
        priority: int = 0,
        timeout: float = 30.0
    ) -> None:
        """Register a shutdown hook"""
        hook = ShutdownHook(
            name=name or handler.__name__,
            handler=handler,
            priority=priority,
            timeout=timeout
        )
        cls._hooks.append(hook)
        # Sort by priority (descending)
        cls._hooks.sort(key=lambda h: h.priority, reverse=True)
    
    @classmethod
    async def shutdown(cls, timeout: float = 60.0) -> None:
        """
        Execute all shutdown hooks
        
        Args:
            timeout: Maximum total shutdown time
        """
        if cls._is_shutting_down:
            logger.warning("Shutdown already in progress")
            return
        
        cls._is_shutting_down = True
        logger.info(f"Starting graceful shutdown ({len(cls._hooks)} hooks)")
        
        start_time = asyncio.get_event_loop().time()
        
        for hook in cls._hooks:
            remaining = timeout - (asyncio.get_event_loop().time() - start_time)
            if remaining <= 0:
                logger.error("Shutdown timeout reached")
                break
            
            hook_timeout = min(hook.timeout, remaining)
            
            try:
                logger.info(f"Executing shutdown hook: {hook.name}")
                await asyncio.wait_for(hook.handler(), timeout=hook_timeout)
                logger.info(f"Shutdown hook completed: {hook.name}")
            except asyncio.TimeoutError:
                logger.error(f"Shutdown hook timed out: {hook.name}")
            except Exception as e:
                logger.exception(f"Shutdown hook failed: {hook.name}: {e}")
        
        logger.info("Graceful shutdown complete")
    
    @classmethod
    def is_shutting_down(cls) -> bool:
        """Check if shutdown is in progress"""
        return cls._is_shutting_down


class StartupManager:
    """
    Manages startup procedures
    """
    
    _hooks: List[StartupHook] = []
    _has_started = False
    
    @classmethod
    def register(
        cls,
        handler: Callable[[], Awaitable[None]],
        name: Optional[str] = None,
        priority: int = 0,
        timeout: float = 30.0
    ) -> None:
        """Register a startup hook"""
        hook = StartupHook(
            name=name or handler.__name__,
            handler=handler,
            priority=priority,
            timeout=timeout
        )
        cls._hooks.append(hook)
        cls._hooks.sort(key=lambda h: h.priority, reverse=True)
    
    @classmethod
    async def startup(cls, timeout: float = 60.0) -> None:
        """Execute all startup hooks"""
        if cls._has_started:
            logger.warning("Startup already completed")
            return
        
        logger.info(f"Starting up ({len(cls._hooks)} hooks)")
        
        start_time = asyncio.get_event_loop().time()
        
        for hook in cls._hooks:
            remaining = timeout - (asyncio.get_event_loop().time() - start_time)
            if remaining <= 0:
                raise TimeoutError("Startup timeout reached")
            
            hook_timeout = min(hook.timeout, remaining)
            
            try:
                logger.info(f"Executing startup hook: {hook.name}")
                await asyncio.wait_for(hook.handler(), timeout=hook_timeout)
                logger.info(f"Startup hook completed: {hook.name}")
            except asyncio.TimeoutError:
                raise TimeoutError(f"Startup hook timed out: {hook.name}")
            except Exception as e:
                logger.exception(f"Startup hook failed: {hook.name}: {e}")
                raise
        
        cls._has_started = True
        logger.info("Startup complete")
    
    @classmethod
    def has_started(cls) -> bool:
        """Check if startup has completed"""
        return cls._has_started


def on_shutdown(
    name: Optional[str] = None,
    priority: int = 0,
    timeout: float = 30.0
):
    """
    Decorator to register a shutdown hook
    
    Args:
        name: Hook name
        priority: Execution priority (higher = first)
        timeout: Maximum execution time
    """
    def decorator(func: Callable[[], Awaitable[None]]):
        ShutdownManager.register(func, name, priority, timeout)
        return func
    return decorator


def on_startup(
    name: Optional[str] = None,
    priority: int = 0,
    timeout: float = 30.0
):
    """
    Decorator to register a startup hook
    
    Args:
        name: Hook name
        priority: Execution priority (higher = first)
        timeout: Maximum execution time
    """
    def decorator(func: Callable[[], Awaitable[None]]):
        StartupManager.register(func, name, priority, timeout)
        return func
    return decorator
