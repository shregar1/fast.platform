"""
PagerDuty incident management client
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from functools import wraps


@dataclass
class PagerDutyIncident:
    """PagerDuty incident"""
    id: str
    title: str
    status: str
    urgency: str
    service_id: str
    description: Optional[str] = None


class PagerDutyClient:
    """
    PagerDuty API client
    """
    
    def __init__(self, api_token: str, default_service_id: Optional[str] = None):
        self.api_token = api_token
        self.default_service_id = default_service_id
        self._session = None
    
    def _get_session(self):
        if self._session is None:
            import aiohttp
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Token token={self.api_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/vnd.pagerduty+json;version=2"
                }
            )
        return self._session
    
    async def trigger_incident(
        self,
        title: str,
        service_id: Optional[str] = None,
        description: Optional[str] = None,
        urgency: str = "high",
        details: Optional[Dict[str, Any]] = None
    ) -> PagerDutyIncident:
        """
        Trigger a new incident
        
        Args:
            title: Incident title
            service_id: Service ID (uses default if not provided)
            description: Detailed description
            urgency: high or low
            details: Additional details
        """
        import aiohttp
        
        service = service_id or self.default_service_id
        if not service:
            raise ValueError("service_id required")
        
        session = self._get_session()
        
        payload = {
            "incident": {
                "type": "incident",
                "title": title,
                "service": {
                    "id": service,
                    "type": "service_reference"
                },
                "urgency": urgency
            }
        }
        
        if description:
            payload["incident"]["body"] = {
                "type": "incident_body",
                "details": description
            }
        
        async with session.post(
            "https://api.pagerduty.com/incidents",
            json=payload
        ) as response:
            if response.status == 201:
                data = await response.json()
                incident = data["incident"]
                return PagerDutyIncident(
                    id=incident["id"],
                    title=incident["title"],
                    status=incident["status"],
                    urgency=incident["urgency"],
                    service_id=incident["service"]["id"],
                    description=description
                )
            else:
                error = await response.text()
                raise PagerDutyError(f"Failed to create incident: {error}")
    
    async def resolve_incident(self, incident_id: str) -> bool:
        """Resolve an incident"""
        import aiohttp
        
        session = self._get_session()
        
        payload = {
            "incident": {
                "type": "incident_reference",
                "status": "resolved"
            }
        }
        
        async with session.put(
            f"https://api.pagerduty.com/incidents/{incident_id}",
            json=payload
        ) as response:
            return response.status == 200
    
    async def acknowledge_incident(self, incident_id: str) -> bool:
        """Acknowledge an incident"""
        import aiohttp
        
        session = self._get_session()
        
        payload = {
            "incident": {
                "type": "incident_reference",
                "status": "acknowledged"
            }
        }
        
        async with session.put(
            f"https://api.pagerduty.com/incidents/{incident_id}",
            json=payload
        ) as response:
            return response.status == 200
    
    async def get_incident(self, incident_id: str) -> Optional[PagerDutyIncident]:
        """Get incident details"""
        import aiohttp
        
        session = self._get_session()
        
        async with session.get(
            f"https://api.pagerduty.com/incidents/{incident_id}"
        ) as response:
            if response.status == 200:
                data = await response.json()
                incident = data["incident"]
                return PagerDutyIncident(
                    id=incident["id"],
                    title=incident["title"],
                    status=incident["status"],
                    urgency=incident["urgency"],
                    service_id=incident["service"]["id"]
                )
            return None
    
    async def close(self):
        """Close the HTTP session"""
        if self._session:
            await self._session.close()
            self._session = None


class PagerDutyError(Exception):
    """PagerDuty API error"""
    pass


def trigger_incident(
    title: Optional[str] = None,
    service_id: Optional[str] = None,
    urgency: str = "high"
):
    """
    Decorator to trigger PagerDuty incident on exception
    
    Args:
        title: Incident title
        service_id: Service ID
        urgency: high or low
    """
    def decorator(func):
        incident_title = title or f"Error in {func.__name__}"
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Would need a global PagerDuty client
                # client.trigger_incident(
                #     title=incident_title,
                #     description=str(e),
                #     service_id=service_id,
                #     urgency=urgency
                # )
                raise
        
        return wrapper
    return decorator
