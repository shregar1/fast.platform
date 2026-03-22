"""Pydantic DTOs for fast-platform configuration (JSON under ``config/<section>/``)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DBConfigurationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")

    user_name: str = ""
    password: str = ""
    host: str = ""
    port: int = 5432
    database: str = ""
    connection_string: str = ""
    async_connection_string: str = ""
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: float = 30.0
    pool_recycle: Optional[int] = None
    pool_pre_ping: bool = True
    connection_name: str = ""
    statement_timeout_seconds: Optional[float] = None
    read_replica_connection_string: str = ""
    read_replica_host: str = ""
    read_replica_port: Optional[int] = None


class VaultSecretsDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    url: str = ""
    token: str = ""
    mount_point: str = "secret"


class AwsSecretsDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    region: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""
    prefix: str = ""


class GcpSecretsDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    project_id: str = ""
    credentials_json_path: str = ""


class SecretsConfigurationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    vault: VaultSecretsDTO = Field(default_factory=VaultSecretsDTO)
    aws: AwsSecretsDTO = Field(default_factory=AwsSecretsDTO)
    gcp: GcpSecretsDTO = Field(default_factory=GcpSecretsDTO)


class RabbitMQConfigDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    url: str = ""
    exchange: str = ""
    default_routing_key: str = ""


class SQSConfigDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    region: str = ""
    queue_url: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""


class NATSConfigDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    servers: List[str] = Field(default_factory=list)
    subject: str = ""


class ServiceBusConfigDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    connection_string: str = ""
    queue_name: str = ""


class QueuesConfigurationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    rabbitmq: RabbitMQConfigDTO = Field(default_factory=RabbitMQConfigDTO)
    sqs: SQSConfigDTO = Field(default_factory=SQSConfigDTO)
    nats: NATSConfigDTO = Field(default_factory=NATSConfigDTO)
    service_bus: ServiceBusConfigDTO = Field(default_factory=ServiceBusConfigDTO)


class CacheConfigurationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    backend: str = "memory"
    default_ttl_seconds: int = 300
    redis_url: str = ""
    namespace: str = "app"


class LLMConfigurationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    default_provider: str = "openai"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"


class OAuthProviderDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    client_id: str = ""
    client_secret: str = ""
    auth_url: str = ""
    token_url: str = ""
    userinfo_url: str = ""
    redirect_uri: str = ""
    scopes: List[str] = Field(default_factory=list)


class IdentityProvidersConfigurationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    google: OAuthProviderDTO = Field(default_factory=OAuthProviderDTO)
    github: OAuthProviderDTO = Field(default_factory=OAuthProviderDTO)
    microsoft: OAuthProviderDTO = Field(default_factory=OAuthProviderDTO)


class PineconeConfigDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    api_key: str = ""
    environment: str = ""
    index_name: str = ""


class QdrantConfigDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    url: str = ""
    api_key: str = ""


class WeaviateConfigDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    url: str = ""
    api_key: str = ""


class VectorsConfigurationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    pinecone: PineconeConfigDTO = Field(default_factory=PineconeConfigDTO)
    qdrant: QdrantConfigDTO = Field(default_factory=QdrantConfigDTO)
    weaviate: WeaviateConfigDTO = Field(default_factory=WeaviateConfigDTO)


class S3StorageDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    bucket: str = ""
    region: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""


class StorageConfigurationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    default_backend: str = "local"
    s3: S3StorageDTO = Field(default_factory=S3StorageDTO)


class MeilisearchDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    host: str = ""
    api_key: str = ""


class SearchConfigurationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    default_backend: str = "meilisearch"
    meilisearch: MeilisearchDTO = Field(default_factory=MeilisearchDTO)


class HttpSinkDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    endpoint: str = ""
    api_key: str = ""


class AnalyticsConfigurationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    http_sink: HttpSinkDTO = Field(default_factory=HttpSinkDTO)


class SnsNotificationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    region: str = ""
    topic_arn: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""


class EventHubsDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    connection_string: str = ""
    event_hub_name: str = ""


class KafkaEventDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    topic: str = ""


class EventBridgeDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    region: str = ""
    bus_name: str = ""
    source: str = ""
    detail_type: str = ""
    access_key_id: str = ""
    secret_access_key: str = ""


class EventsConfigurationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    sns: SnsNotificationDTO = Field(default_factory=SnsNotificationDTO)
    event_hubs: EventHubsDTO = Field(default_factory=EventHubsDTO)
    kafka: KafkaEventDTO = Field(default_factory=KafkaEventDTO)
    event_bridge: EventBridgeDTO = Field(default_factory=EventBridgeDTO)


class TelemetryConfigurationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    service_name: str = "fastmvc"
    exporter: str = "otlp"
    otlp_endpoint: str = ""


class DatadogConfigurationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    api_key: str = ""
    site: str = "datadoghq.com"


class StreamsConfigurationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = True
    tick_history: int = 1000
    fanout_queue_backend: str = ""
    backpressure_mode: str = "drop_oldest"


__all__ = [
    "AnalyticsConfigurationDTO",
    "CacheConfigurationDTO",
    "DBConfigurationDTO",
    "DatadogConfigurationDTO",
    "EventsConfigurationDTO",
    "EventBridgeDTO",
    "EventHubsDTO",
    "GcpSecretsDTO",
    "HttpSinkDTO",
    "IdentityProvidersConfigurationDTO",
    "KafkaEventDTO",
    "LLMConfigurationDTO",
    "MeilisearchDTO",
    "NATSConfigDTO",
    "OAuthProviderDTO",
    "PineconeConfigDTO",
    "QdrantConfigDTO",
    "QueuesConfigurationDTO",
    "RabbitMQConfigDTO",
    "SearchConfigurationDTO",
    "SecretsConfigurationDTO",
    "ServiceBusConfigDTO",
    "SnsNotificationDTO",
    "SQSConfigDTO",
    "StorageConfigurationDTO",
    "StreamsConfigurationDTO",
    "TelemetryConfigurationDTO",
    "VaultSecretsDTO",
    "VectorsConfigurationDTO",
    "WeaviateConfigDTO",
    "AwsSecretsDTO",
]
