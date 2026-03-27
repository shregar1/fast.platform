"""
Discord webhook client
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DiscordEmbed:
    """Discord embed message"""
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    color: Optional[int] = None  # Hex color code
    timestamp: Optional[str] = None
    footer: Optional[Dict[str, str]] = None
    image: Optional[Dict[str, str]] = None
    thumbnail: Optional[Dict[str, str]] = None
    author: Optional[Dict[str, str]] = None
    fields: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        data = {}
        if self.title:
            data["title"] = self.title
        if self.description:
            data["description"] = self.description
        if self.url:
            data["url"] = self.url
        if self.color:
            data["color"] = self.color
        if self.timestamp:
            data["timestamp"] = self.timestamp
        if self.footer:
            data["footer"] = self.footer
        if self.image:
            data["image"] = self.image
        if self.thumbnail:
            data["thumbnail"] = self.thumbnail
        if self.author:
            data["author"] = self.author
        if self.fields:
            data["fields"] = self.fields
        return data


class DiscordClient:
    """
    Discord webhook client
    """
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_message(
        self,
        content: Optional[str] = None,
        username: Optional[str] = None,
        avatar_url: Optional[str] = None,
        embeds: Optional[List[DiscordEmbed]] = None,
        tts: bool = False
    ) -> bool:
        """
        Send a message to Discord
        
        Args:
            content: Message text (max 2000 chars)
            username: Override webhook username
            avatar_url: Override webhook avatar
            embeds: Rich embeds (max 10)
            tts: Text-to-speech
        """
        import aiohttp
        
        payload = {}
        
        if content:
            payload["content"] = content[:2000]  # Discord limit
        if username:
            payload["username"] = username
        if avatar_url:
            payload["avatar_url"] = avatar_url
        if embeds:
            payload["embeds"] = [e.to_dict() for e in embeds[:10]]
        if tts:
            payload["tts"] = tts
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                return response.status in (200, 204)
    
    async def send_simple(
        self,
        message: str,
        username: Optional[str] = None
    ) -> bool:
        """Send a simple text message"""
        return await self.send_message(content=message, username=username)
    
    async def send_embed(
        self,
        title: str,
        description: str,
        color: int = 0x3498db,
        fields: Optional[List[Dict]] = None,
        username: Optional[str] = None
    ) -> bool:
        """Send an embed message"""
        embed = DiscordEmbed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow().isoformat(),
            fields=fields or []
        )
        return await self.send_message(embeds=[embed], username=username)
    
    async def send_success(self, title: str, description: str) -> bool:
        """Send success notification (green)"""
        return await self.send_embed(title, description, color=0x2ecc71)
    
    async def send_error(self, title: str, description: str) -> bool:
        """Send error notification (red)"""
        return await self.send_embed(title, description, color=0xe74c3c)
    
    async def send_warning(self, title: str, description: str) -> bool:
        """Send warning notification (yellow)"""
        return await self.send_embed(title, description, color=0xf39c12)
    
    async def send_info(self, title: str, description: str) -> bool:
        """Send info notification (blue)"""
        return await self.send_embed(title, description, color=0x3498db)
    
    async def send_deployment_notification(
        self,
        service: str,
        version: str,
        environment: str,
        status: str = "success",
        commit_sha: Optional[str] = None,
        author: Optional[str] = None
    ) -> bool:
        """Send deployment notification"""
        color = 0x2ecc71 if status == "success" else 0xe74c3c
        
        fields = [
            {"name": "Service", "value": service, "inline": True},
            {"name": "Version", "value": version, "inline": True},
            {"name": "Environment", "value": environment, "inline": True},
        ]
        
        if commit_sha:
            fields.append({"name": "Commit", "value": commit_sha[:7], "inline": True})
        if author:
            fields.append({"name": "Author", "value": author, "inline": True})
        
        embed = DiscordEmbed(
            title=f"🚀 Deployment {status.upper()}",
            description=f"Deployment to {environment} completed {status}fully",
            color=color,
            timestamp=datetime.utcnow().isoformat(),
            fields=fields
        )
        
        return await self.send_message(embeds=[embed])
