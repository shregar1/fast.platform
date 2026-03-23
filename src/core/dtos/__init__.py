"""Configuration DTOs (one class per module)."""

from __future__ import annotations

from .abstraction import IDTO
from .analytics import AnalyticsConfigurationDTO
from .aws_secrets import AwsSecretsDTO
from .cache import CacheConfigurationDTO
from .celery_jobs import CeleryJobsDTO
from .datadog import DatadogConfigurationDTO
from .db import DBConfigurationDTO
from .dramatiq_jobs import DramatiqJobsDTO
from .event_bridge import EventBridgeDTO
from .event_hubs import EventHubsDTO
from .events import EventsConfigurationDTO
from .feature_flags import FeatureFlagsConfigurationDTO
from .feature_flags_snapshot import FeatureFlagsSnapshotDTO
from .gcp_secrets import GcpSecretsDTO
from .http_sink import HttpSinkDTO
from .identity_providers import IdentityProvidersConfigurationDTO
from .jobs import JobsConfigurationDTO
from .kafka_event import KafkaEventDTO
from .launchdarkly_feature_flags import LaunchDarklyFeatureFlagsDTO
from .llm import LLMConfigurationDTO
from .meilisearch import MeilisearchDTO
from .nats_config import NATSConfigDTO
from .oauth_provider import OAuthProviderDTO
from .pinecone_config import PineconeConfigDTO
from .qdrant_config import QdrantConfigDTO
from .queues import QueuesConfigurationDTO
from .rabbit_mq_config import RabbitMQConfigDTO
from .realtime import RealtimeConfigurationDTO
from .rq_jobs import RqJobsDTO
from .s3_storage import S3StorageDTO
from .scheduler_jobs import SchedulerJobsDTO
from .search import SearchConfigurationDTO
from .secrets import SecretsConfigurationDTO
from .service_bus_config import ServiceBusConfigDTO
from .sns_notification import SnsNotificationDTO
from .sqs_config import SQSConfigDTO
from .storage import StorageConfigurationDTO
from .streams import StreamsConfigurationDTO
from .telemetry import TelemetryConfigurationDTO
from .unleash_feature_flags import UnleashFeatureFlagsDTO
from .vault_secrets import VaultSecretsDTO
from .vectors import VectorsConfigurationDTO
from .weaviate_config import WeaviateConfigDTO
from .webrtc_ice_config import WebRtcIceConfigDTO
from .webrtc_ice_server import WebRtcIceServerDTO

__all__ = [
    "IDTO",
    "AnalyticsConfigurationDTO",
    "AwsSecretsDTO",
    "CacheConfigurationDTO",
    "CeleryJobsDTO",
    "DatadogConfigurationDTO",
    "DBConfigurationDTO",
    "DramatiqJobsDTO",
    "EventBridgeDTO",
    "EventHubsDTO",
    "EventsConfigurationDTO",
    "FeatureFlagsConfigurationDTO",
    "FeatureFlagsSnapshotDTO",
    "GcpSecretsDTO",
    "HttpSinkDTO",
    "IdentityProvidersConfigurationDTO",
    "JobsConfigurationDTO",
    "KafkaEventDTO",
    "LaunchDarklyFeatureFlagsDTO",
    "LLMConfigurationDTO",
    "MeilisearchDTO",
    "NATSConfigDTO",
    "OAuthProviderDTO",
    "PineconeConfigDTO",
    "QdrantConfigDTO",
    "QueuesConfigurationDTO",
    "RabbitMQConfigDTO",
    "RealtimeConfigurationDTO",
    "RqJobsDTO",
    "S3StorageDTO",
    "SchedulerJobsDTO",
    "SearchConfigurationDTO",
    "SecretsConfigurationDTO",
    "ServiceBusConfigDTO",
    "SnsNotificationDTO",
    "SQSConfigDTO",
    "StorageConfigurationDTO",
    "StreamsConfigurationDTO",
    "TelemetryConfigurationDTO",
    "UnleashFeatureFlagsDTO",
    "VaultSecretsDTO",
    "VectorsConfigurationDTO",
    "WeaviateConfigDTO",
    "WebRtcIceConfigDTO",
    "WebRtcIceServerDTO",
]
