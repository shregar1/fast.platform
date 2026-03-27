"""
Datadog API client
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class DatadogConfig:
    """Datadog configuration"""
    api_key: str
    app_key: Optional[str] = None
    api_url: str = "https://api.datadoghq.com"
    site: str = "datadoghq.com"


class DatadogClient:
    """
    Datadog API client
    """
    
    def __init__(self, api_key: str, app_key: Optional[str] = None, site: Optional[str] = None):
        self.config = DatadogConfig(
            api_key=api_key,
            app_key=app_key,
            site=site or "datadoghq.com"
        )
        self._api = None
    
    def _get_api(self):
        if self._api is None:
            try:
                import datadog
                from datadog import api, initialize
                
                options = {
                    "api_key": self.config.api_key,
                    "app_key": self.config.app_key
                }
                
                if self.config.site != "datadoghq.com":
                    options["api_host"] = f"https://api.{self.config.site}"
                
                initialize(**options)
                self._api = api
                
            except ImportError:
                raise ImportError("datadog package required for DatadogClient")
        
        return self._api
    
    async def send_metric(
        self,
        metric_name: str,
        value: float,
        tags: Optional[List[str]] = None,
        metric_type: str = "gauge"
    ) -> bool:
        """Send a metric to Datadog"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        api = self._get_api()
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(
                pool,
                lambda: api.Metric.send(
                    metric=metric_name,
                    points=[(int(asyncio.get_event_loop().time()), value)],
                    tags=tags or [],
                    type=metric_type
                )
            )
        
        return result.get("status", "ok") == "ok"
    
    async def send_event(
        self,
        title: str,
        text: str,
        alert_type: str = "info",
        tags: Optional[List[str]] = None
    ) -> bool:
        """Send an event to Datadog"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        api = self._get_api()
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(
                pool,
                lambda: api.Event.create(
                    title=title,
                    text=text,
                    alert_type=alert_type,
                    tags=tags or []
                )
            )
        
        return "id" in result
    
    async def send_log(
        self,
        message: str,
        level: str = "info",
        service: Optional[str] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Send a log to Datadog"""
        import aiohttp
        
        url = f"https://http-intake.logs.{self.config.site}/v1/input"
        
        headers = {
            "Content-Type": "application/json",
            "DD-API-KEY": self.config.api_key
        }
        
        payload = {
            "message": message,
            "level": level,
            "service": service,
            "source": source,
            "ddtags": ",".join(tags) if tags else ""
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                return response.status == 200
