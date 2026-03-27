"""Datadog APM (Application Performance Monitoring)."""

from typing import Optional, Dict, Any, Callable
from functools import wraps
import time


def trace_operation(
    operation_name: Optional[str] = None,
    service: Optional[str] = None,
    resource: Optional[str] = None,
    span_type: Optional[str] = None,
):
    """Decorator to trace function execution with Datadog APM.

    Args:
        operation_name: Name of the operation
        service: Service name
        resource: Resource name
        span_type: Type of span (e.g., "web", "db", "cache")

    """

    def decorator(func: Callable):
        """Execute decorator operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """
        name = operation_name or func.__name__

        @wraps(func)
        async def wrapper(*args, **kwargs):
            """Execute wrapper operation.

            Returns:
                The result of the operation.
            """
            # Try to import ddtrace
            try:
                from ddtrace import tracer

                with tracer.trace(
                    name, service=service, resource=resource, span_type=span_type
                ) as span:
                    # Add arguments as tags (sanitized)
                    for key, value in kwargs.items():
                        if isinstance(value, (str, int, float, bool)):
                            span.set_tag(f"arg.{key}", value)

                    try:
                        result = await func(*args, **kwargs)
                        span.set_tag("status", "success")
                        return result
                    except Exception as e:
                        span.set_tag("status", "error")
                        span.set_tag("error.message", str(e))
                        raise

            except ImportError:
                # ddtrace not installed, just run the function
                return await func(*args, **kwargs)

        return wrapper

    return decorator


class DatadogTracer:
    """Datadog tracer wrapper."""

    def __init__(self):
        """Execute __init__ operation."""
        self._tracer = None

    def _get_tracer(self):
        """Execute _get_tracer operation.

        Returns:
            The result of the operation.
        """
        if self._tracer is None:
            try:
                from ddtrace import tracer

                self._tracer = tracer
            except ImportError:
                raise ImportError("ddtrace package required for DatadogTracer")
        return self._tracer

    def start_span(
        self,
        name: str,
        service: Optional[str] = None,
        resource: Optional[str] = None,
        span_type: Optional[str] = None,
    ) -> Any:
        """Start a new span."""
        tracer = self._get_tracer()
        return tracer.trace(name, service=service, resource=resource, span_type=span_type)

    def current_span(self) -> Optional[Any]:
        """Get current active span."""
        try:
            tracer = self._get_tracer()
            return tracer.current_span()
        except Exception:
            return None

    def inject_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Inject tracing headers for distributed tracing."""
        try:
            from ddtrace.propagation.http import HTTPPropagator

            tracer = self._get_tracer()

            if tracer.current_span():
                HTTPPropagator.inject(headers, tracer.current_span().context)

            return headers
        except ImportError:
            return headers
