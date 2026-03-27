"""
OneSignal API client for push notifications
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class DeviceType(Enum):
    """OneSignal device types"""
    IOS = 0
    ANDROID = 1
    AMAZON = 2
    WINDOWS_PHONE = 3
    CHROME_APP = 4
    CHROME_WEB = 5
    WINDOWS = 6
    FIREFOX = 7
    MACOS = 8
    HUAWEI = 13


@dataclass
class OneSignalNotification:
    """OneSignal notification"""
    id: str
    recipients: int
    errors: Optional[Dict[str, Any]] = None


class OneSignalClient:
    """
    OneSignal API client
    """
    
    def __init__(self, app_id: str, rest_api_key: str):
        self.app_id = app_id
        self.rest_api_key = rest_api_key
        self.base_url = "https://onesignal.com/api/v1"
    
    async def send_to_all(
        self,
        headings: Dict[str, str],  # {"en": "Title"}
        contents: Dict[str, str],  # {"en": "Message"}
        data: Optional[Dict[str, Any]] = None,
        buttons: Optional[List[Dict[str, str]]] = None,
        url: Optional[str] = None,
        send_after: Optional[str] = None
    ) -> OneSignalNotification:
        """
        Send notification to all subscribed users
        
        Args:
            headings: Notification title by language
            contents: Notification body by language
            data: Additional data payload
            buttons: Action buttons
            url: URL to open on click
            send_after: Schedule time (ISO 8601)
        """
        import aiohttp
        
        url_endpoint = f"{self.base_url}/notifications"
        
        payload = {
            "app_id": self.app_id,
            "included_segments": ["All"],
            "headings": headings,
            "contents": contents
        }
        
        if data:
            payload["data"] = data
        if buttons:
            payload["buttons"] = buttons
        if url:
            payload["url"] = url
        if send_after:
            payload["send_after"] = send_after
        
        headers = {
            "Authorization": f"Basic {self.rest_api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url_endpoint,
                json=payload,
                headers=headers
            ) as response:
                data = await response.json()
                
                if "errors" in data:
                    raise OneSignalError(data["errors"])
                
                return OneSignalNotification(
                    id=data["id"],
                    recipients=data.get("recipients", 0),
                    errors=data.get("errors")
                )
    
    async def send_to_users(
        self,
        player_ids: List[str],
        headings: Dict[str, str],
        contents: Dict[str, str],
        data: Optional[Dict[str, Any]] = None
    ) -> OneSignalNotification:
        """Send to specific users by player ID"""
        import aiohttp
        
        url = f"{self.base_url}/notifications"
        
        payload = {
            "app_id": self.app_id,
            "include_player_ids": player_ids,
            "headings": headings,
            "contents": contents
        }
        
        if data:
            payload["data"] = data
        
        headers = {
            "Authorization": f"Basic {self.rest_api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                data = await response.json()
                
                if "errors" in data:
                    raise OneSignalError(data["errors"])
                
                return OneSignalNotification(
                    id=data["id"],
                    recipients=data.get("recipients", 0)
                )
    
    async def send_to_segments(
        self,
        segments: List[str],
        headings: Dict[str, str],
        contents: Dict[str, str]
    ) -> OneSignalNotification:
        """Send to specific segments"""
        import aiohttp
        
        url = f"{self.base_url}/notifications"
        
        payload = {
            "app_id": self.app_id,
            "included_segments": segments,
            "headings": headings,
            "contents": contents
        }
        
        headers = {
            "Authorization": f"Basic {self.rest_api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                data = await response.json()
                
                if "errors" in data:
                    raise OneSignalError(data["errors"])
                
                return OneSignalNotification(
                    id=data["id"],
                    recipients=data.get("recipients", 0)
                )
    
    async def send_to_tags(
        self,
        tags: List[Dict[str, Any]],  # [{"key": "role", "relation": "=", "value": "admin"}]
        headings: Dict[str, str],
        contents: Dict[str, str]
    ) -> OneSignalNotification:
        """Send to users matching tags"""
        import aiohttp
        
        url = f"{self.base_url}/notifications"
        
        payload = {
            "app_id": self.app_id,
            "filters": tags,
            "headings": headings,
            "contents": contents
        }
        
        headers = {
            "Authorization": f"Basic {self.rest_api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                data = await response.json()
                
                if "errors" in data:
                    raise OneSignalError(data["errors"])
                
                return OneSignalNotification(
                    id=data["id"],
                    recipients=data.get("recipients", 0)
                )
    
    async def cancel_notification(self, notification_id: str) -> bool:
        """Cancel a scheduled notification"""
        import aiohttp
        
        url = f"{self.base_url}/notifications/{notification_id}?app_id={self.app_id}"
        
        headers = {
            "Authorization": f"Basic {self.rest_api_key}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as response:
                return response.status == 200
    
    async def get_notification(self, notification_id: str) -> Dict[str, Any]:
        """Get notification details"""
        import aiohttp
        
        url = f"{self.base_url}/notifications/{notification_id}?app_id={self.app_id}"
        
        headers = {
            "Authorization": f"Basic {self.rest_api_key}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                return await response.json()
    
    async def get_devices(self, limit: int = 300) -> List[Dict[str, Any]]:
        """Get list of devices"""
        import aiohttp
        
        url = f"{self.base_url}/players?app_id={self.app_id}&limit={limit}"
        
        headers = {
            "Authorization": f"Basic {self.rest_api_key}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                data = await response.json()
                return data.get("players", [])
    
    async def create_segment(
        self,
        name: str,
        filters: List[Dict[str, Any]]
    ) -> str:
        """Create a new segment"""
        import aiohttp
        
        url = f"{self.base_url}/apps/{self.app_id}/segments"
        
        payload = {
            "name": name,
            "filters": filters
        }
        
        headers = {
            "Authorization": f"Basic {self.rest_api_key}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                data = await response.json()
                return data.get("id")


class OneSignalError(Exception):
    """OneSignal API error"""
    pass
