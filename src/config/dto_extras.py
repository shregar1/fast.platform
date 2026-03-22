"""Additional configuration DTOs (jobs, WebRTC / realtime)."""

from __future__ import annotations

from typing import Any, Dict, List, Union

from pydantic import BaseModel, ConfigDict, Field


class CeleryJobsDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    broker_url: str = ""
    result_backend: str = ""
    namespace: str = "fastmvc"


class RqJobsDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    connection_url: str = ""
    redis_url: str = ""
    queue_name: str = "default"


class DramatiqJobsDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    broker_url: str = ""


class SchedulerJobsDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False


class JobsConfigurationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    celery: CeleryJobsDTO = Field(default_factory=CeleryJobsDTO)
    rq: RqJobsDTO = Field(default_factory=RqJobsDTO)
    dramatiq: DramatiqJobsDTO = Field(default_factory=DramatiqJobsDTO)
    scheduler: SchedulerJobsDTO = Field(default_factory=SchedulerJobsDTO)
    queue_timeouts: Dict[str, int] = Field(default_factory=dict)


class WebRtcIceServerDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    urls: Union[str, List[str]] = ""
    username: str = ""
    credential: str = ""


class WebRtcIceConfigDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    ice_servers: List[WebRtcIceServerDTO] = Field(default_factory=list)


class RealtimeConfigurationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    webrtc: WebRtcIceConfigDTO = Field(default_factory=WebRtcIceConfigDTO)


class FeatureFlagsSnapshotDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    path: str = ""


class LaunchDarklyFeatureFlagsDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    sdk_key: str = ""
    default_user_key: str = "anonymous"


class UnleashFeatureFlagsDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    url: str = ""
    app_name: str = ""
    instance_id: str = ""
    api_key: str = ""


class FeatureFlagsConfigurationDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    snapshot: FeatureFlagsSnapshotDTO = Field(default_factory=FeatureFlagsSnapshotDTO)
    launchdarkly: LaunchDarklyFeatureFlagsDTO = Field(default_factory=LaunchDarklyFeatureFlagsDTO)
    unleash: UnleashFeatureFlagsDTO = Field(default_factory=UnleashFeatureFlagsDTO)


__all__ = [
    "CeleryJobsDTO",
    "DramatiqJobsDTO",
    "FeatureFlagsConfigurationDTO",
    "FeatureFlagsSnapshotDTO",
    "JobsConfigurationDTO",
    "LaunchDarklyFeatureFlagsDTO",
    "RealtimeConfigurationDTO",
    "RqJobsDTO",
    "SchedulerJobsDTO",
    "UnleashFeatureFlagsDTO",
    "WebRtcIceConfigDTO",
    "WebRtcIceServerDTO",
]
