"""Single WebRTC ICE server entry."""

from __future__ import annotations

from typing import List, Union

from pydantic import ConfigDict

from .abstraction import IDTO


class WebRtcIceServerDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    urls: Union[str, List[str]] = ""
    username: str = ""
    credential: str = ""
