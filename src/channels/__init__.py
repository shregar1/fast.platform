"""
fast_channels – Real-time channels extension for FastMVC.
"""

from __future__ import annotations

from .acl import (
    AllowAllChannelACL,
    ChannelACLPolicy,
    StaticChannelACL,
    make_subscribe_acl_checker,
)
from .base import IChannelBackend
from .config_loader import ChannelsConfiguration
from .dto import ChannelsConfigurationDTO
from .heartbeat import run_heartbeat_loop
from .hub import ChannelsHub
from .metrics import ChannelMetrics, InMemoryChannelMetrics
from .kafka_backend import KafkaChannelBackend
from .presence import (
    InMemoryPresenceBackend,
    PresenceEntry,
    PresenceService,
    RedisPresenceBackend,
)
from .redis_backend import RedisChannelBackend
from .subscriber_counters import InMemorySubscriberCounters, RedisSubscriberCounters

__all__ = [
    "AllowAllChannelACL",
    "ChannelACLPolicy",
    "IChannelBackend",
    "ChannelMetrics",
    "ChannelsConfiguration",
    "ChannelsConfigurationDTO",
    "ChannelsHub",
    "InMemoryChannelMetrics",
    "InMemoryPresenceBackend",
    "InMemorySubscriberCounters",
    "KafkaChannelBackend",
    "PresenceEntry",
    "PresenceService",
    "RedisChannelBackend",
    "RedisPresenceBackend",
    "RedisSubscriberCounters",
    "StaticChannelACL",
    "make_subscribe_acl_checker",
    "run_heartbeat_loop",
]
