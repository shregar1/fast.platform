"""
Retry policy implementation
"""

from typing import Optional, Callable, Any, Type
from dataclasses import dataclass
from functools import wraps
import random
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class RetryPolicy:
    """Retry policy configuration"""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    
    # Exceptions to retry on
    retry_on: tuple = (Exception,)
    
    # Exceptions to not retry on
    dont_retry_on: tuple = ()
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for attempt"""
        delay = self.initial_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            delay = delay * (0.5 + random.random())
        
        return delay
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Check if we should retry"""
        if attempt >= self.max_attempts:
            return False
        
        if isinstance(exception, self.dont_retry_on):
            return False
        
        return isinstance(exception, self.retry_on)


class RetryExceeded(Exception):
    """Raised when all retry attempts are exhausted"""
    pass


def retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retry_on: tuple = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator to add retry logic to a function
    
    Args:
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay between retries
        max_delay: Maximum delay between retries
        exponential_base: Exponential backoff base
        retry_on: Exceptions to retry on
        on_retry: Callback on each retry
    """
    def decorator(func: Callable):
        policy = RetryPolicy(
            max_attempts=max_attempts,
            initial_delay=initial_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            retry_on=retry_on
        )
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if not policy.should_retry(e, attempt):
                        raise
                    
                    if attempt < max_attempts - 1:
                        delay = policy.get_delay(attempt)
                        
                        if on_retry:
                            on_retry(e, attempt + 1)
                        
                        logger.warning(
                            f"Retry {attempt + 1}/{max_attempts} for {func.__name__} "
                            f"after {delay:.1f}s: {e}"
                        )
                        
                        await asyncio.sleep(delay)
            
            raise RetryExceeded(
                f"Failed after {max_attempts} attempts"
            ) from last_exception
        
        return wrapper
    return decorator
