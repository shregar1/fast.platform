"""
Telegram Bot API client
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class TelegramMessage:
    """Telegram message"""
    message_id: int
    chat_id: int
    text: str
    date: int


class TelegramClient:
    """
    Telegram Bot API client
    """
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        parse_mode: Optional[str] = "HTML",  # HTML, Markdown, MarkdownV2
        disable_web_page_preview: bool = False,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None
    ) -> TelegramMessage:
        """
        Send a text message
        
        Args:
            chat_id: Chat ID or channel username (@channelname)
            text: Message text (max 4096 chars)
            parse_mode: Message format
        """
        import aiohttp
        
        url = f"{self.base_url}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": text[:4096],
            "disable_web_page_preview": disable_web_page_preview,
            "disable_notification": disable_notification
        }
        
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                data = await response.json()
                
                if not data.get("ok"):
                    raise TelegramError(data.get("description", "Unknown error"))
                
                result = data["result"]
                return TelegramMessage(
                    message_id=result["message_id"],
                    chat_id=result["chat"]["id"],
                    text=result.get("text", ""),
                    date=result["date"]
                )
    
    async def send_photo(
        self,
        chat_id: int | str,
        photo: str,  # URL or file_id
        caption: Optional[str] = None,
        parse_mode: Optional[str] = "HTML"
    ) -> TelegramMessage:
        """Send a photo"""
        import aiohttp
        
        url = f"{self.base_url}/sendPhoto"
        
        payload = {
            "chat_id": chat_id,
            "photo": photo
        }
        
        if caption:
            payload["caption"] = caption[:1024]
        if parse_mode:
            payload["parse_mode"] = parse_mode
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                data = await response.json()
                
                if not data.get("ok"):
                    raise TelegramError(data.get("description"))
                
                result = data["result"]
                return TelegramMessage(
                    message_id=result["message_id"],
                    chat_id=result["chat"]["id"],
                    text=result.get("caption", ""),
                    date=result["date"]
                )
    
    async def send_document(
        self,
        chat_id: int | str,
        document: str,  # URL or file_id
        caption: Optional[str] = None
    ) -> TelegramMessage:
        """Send a document"""
        import aiohttp
        
        url = f"{self.base_url}/sendDocument"
        
        payload = {
            "chat_id": chat_id,
            "document": document
        }
        
        if caption:
            payload["caption"] = caption[:1024]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                data = await response.json()
                
                if not data.get("ok"):
                    raise TelegramError(data.get("description"))
                
                result = data["result"]
                return TelegramMessage(
                    message_id=result["message_id"],
                    chat_id=result["chat"]["id"],
                    text=result.get("caption", ""),
                    date=result["date"]
                )
    
    async def send_poll(
        self,
        chat_id: int | str,
        question: str,
        options: List[str],
        is_anonymous: bool = True
    ) -> Dict[str, Any]:
        """Send a poll"""
        import aiohttp
        
        url = f"{self.base_url}/sendPoll"
        
        payload = {
            "chat_id": chat_id,
            "question": question,
            "options": [{"text": opt} for opt in options[:10]],  # Max 10 options
            "is_anonymous": is_anonymous
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                data = await response.json()
                
                if not data.get("ok"):
                    raise TelegramError(data.get("description"))
                
                return data["result"]
    
    async def get_updates(
        self,
        offset: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get bot updates"""
        import aiohttp
        
        url = f"{self.base_url}/getUpdates"
        params = {"limit": limit}
        
        if offset:
            params["offset"] = offset
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                
                if not data.get("ok"):
                    raise TelegramError(data.get("description"))
                
                return data["result"]
    
    async def set_webhook(self, url: str) -> bool:
        """Set webhook for receiving updates"""
        import aiohttp
        
        webhook_url = f"{self.base_url}/setWebhook"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json={"url": url}) as response:
                data = await response.json()
                return data.get("ok", False)
    
    async def delete_webhook(self) -> bool:
        """Delete webhook"""
        import aiohttp
        
        url = f"{self.base_url}/deleteWebhook"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url) as response:
                data = await response.json()
                return data.get("ok", False)


class TelegramError(Exception):
    """Telegram API error"""
    pass
