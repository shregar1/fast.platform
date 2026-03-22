"""Additional configuration DTOs (jobs, WebRTC / realtime)."""

from __future__ import annotations

from typing import Any, Dict, List, Union

from pydantic import BaseModel, ConfigDict, Field


class CeleryJobsDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    broker_url: str = ""


class RqJobsDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    connection_url: str = ""


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


__all__ = [
    "CeleryJobsDTO",
    "DramatiqJobsDTO",
    "JobsConfigurationDTO",
    "RealtimeConfigurationDTO",
    "RqJobsDTO",
    "SchedulerJobsDTO",
    "WebRtcIceConfigDTO",
    "WebRtcIceServerDTO",
]
