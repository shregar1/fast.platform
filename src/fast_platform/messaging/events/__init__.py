"""Cloud event bus helpers (SNS, EventBridge, Event Hubs, Kafka); configuration via :mod:`fast_platform.configuration`."""

from .bus import (
    IEventBus,
    INotificationBus,
    build_event_bus,
    build_notification_bus,
)
from .decorators import (
    Event,
    EventBus,
    BackgroundEventRunner,
    EventRecorder,
    event,
    on,
    emit,
    publish,
    get_event_bus,
)

__all__ = [
    # Bus
    "IEventBus",
    "INotificationBus",
    "build_event_bus",
    "build_notification_bus",
    # Decorators
    "Event",
    "EventBus",
    "BackgroundEventRunner",
    "EventRecorder",
    "event",
    "on",
    "emit",
    "publish",
    "get_event_bus",
]
