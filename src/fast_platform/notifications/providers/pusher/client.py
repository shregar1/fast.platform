"""
Pusher API client for real-time notifications
"""

from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass


@dataclass
class PusherChannel:
    """Pusher channel"""
    name: str
    is_private: bool = False
    is_presence: bool = False


class PusherClient:
    """
    Pusher client for real-time notifications
    """
    
    def __init__(
        self,
        app_id: str,
        key: str,
        secret: str,
        cluster: str = "mt1",
        ssl: bool = True
    ):
        self.app_id = app_id
        self.key = key
        self.secret = secret
        self.cluster = cluster
        self.ssl = ssl
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                import pusher
                
                self._client = pusher.Pusher(
                    app_id=self.app_id,
                    key=self.key,
                    secret=self.secret,
                    cluster=self.cluster,
                    ssl=self.ssl
                )
            except ImportError:
                raise ImportError("pusher package required for PusherClient")
        
        return self._client
    
    async def trigger(
        self,
        channels: List[str],
        event: str,
        data: Dict[str, Any],
        socket_id: Optional[str] = None
    ) -> bool:
        """
        Trigger an event on one or more channels
        
        Args:
            channels: List of channel names
            event: Event name
            data: Event data
            socket_id: Exclude this socket ID from receiving the event
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        kwargs = {
            "channels": channels,
            "event_name": event,
            "data": data
        }
        
        if socket_id:
            kwargs["socket_id"] = socket_id
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool,
                lambda: client.trigger(**kwargs)
            )
        
        return True
    
    async def trigger_batch(self, events: List[Dict[str, Any]]) -> bool:
        """Trigger multiple events in a single request"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(
                pool,
                lambda: client.trigger_batch(batch=events)
            )
        
        return True
    
    async def authenticate_private_channel(
        self,
        socket_id: str,
        channel_name: str
    ) -> Dict[str, str]:
        """
        Authenticate a private channel
        
        Returns auth signature for the client
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            auth = await loop.run_in_executor(
                pool,
                lambda: client.authenticate(
                    channel=channel_name,
                    socket_id=socket_id
                )
            )
        
        return auth
    
    async def authenticate_presence_channel(
        self,
        socket_id: str,
        channel_name: str,
        user_id: str,
        user_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Authenticate a presence channel
        
        Args:
            socket_id: Socket ID
            channel_name: Channel name
            user_id: User ID
            user_info: Additional user info
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        auth_data = {
            "user_id": user_id
        }
        
        if user_info:
            auth_data["user_info"] = user_info
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            auth = await loop.run_in_executor(
                pool,
                lambda: client.authenticate(
                    channel=channel_name,
                    socket_id=socket_id,
                    custom_data=auth_data
                )
            )
        
        return auth
    
    async def get_channel_info(
        self,
        channel_name: str,
        info_attributes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get channel information"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        params = {}
        if info_attributes:
            params["info"] = ",".join(info_attributes)
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            info = await loop.run_in_executor(
                pool,
                lambda: client.channel_info(channel_name, params)
            )
        
        return info
    
    async def get_channels(
        self,
        prefix_filter: Optional[str] = None,
        info_attributes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get all active channels"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        params = {}
        if prefix_filter:
            params["filter_by_prefix"] = prefix_filter
        if info_attributes:
            params["info"] = ",".join(info_attributes)
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            channels = await loop.run_in_executor(
                pool,
                lambda: client.channels_info(params)
            )
        
        return channels
    
    async def get_users_in_channel(self, channel_name: str) -> List[Dict[str, Any]]:
        """Get users in a presence channel"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        client = self._get_client()
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            users = await loop.run_in_executor(
                pool,
                lambda: client.users_info(channel_name)
            )
        
        return users.get("users", [])
    
    def webhook_handler(
        self,
        webhook_secret: str
    ) -> Callable:
        """
        Create a webhook handler for Pusher events
        
        Returns a decorator that validates webhook signatures
        """
        def decorator(func: Callable):
            import hmac
            import hashlib
            
            async def wrapper(request):
                # Get signature from header
                signature = request.headers.get("X-Pusher-Signature")
                body = await request.body()
                
                # Verify signature
                expected = hmac.new(
                    webhook_secret.encode(),
                    body,
                    hashlib.sha256
                ).hexdigest()
                
                if not hmac.compare_digest(signature, expected):
                    raise ValueError("Invalid webhook signature")
                
                # Parse and handle events
                events = await request.json()
                return await func(events)
            
            return wrapper
        return decorator
