"""WhatsApp Business API client."""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class MessageType(str, Enum):
    """WhatsApp message types."""

    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    LOCATION = "location"
    CONTACTS = "contacts"
    INTERACTIVE = "interactive"
    TEMPLATE = "template"


@dataclass
class WhatsAppMessage:
    """WhatsApp message."""

    id: str
    status: str
    recipient: str


class WhatsAppClient:
    """WhatsApp Business API client (Meta/Facebook)."""

    def __init__(self, phone_number_id: str, access_token: str):
        """Execute __init__ operation.

        Args:
            phone_number_id: The phone_number_id parameter.
            access_token: The access_token parameter.
        """
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.base_url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"

    async def send_text(
        self,
        to: str,  # Phone number with country code
        body: str,
        preview_url: bool = False,
    ) -> WhatsAppMessage:
        """Send a text message."""
        import aiohttp

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": preview_url, "body": body},
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, json=payload, headers=headers) as response:
                data = await response.json()

                if response.status != 200:
                    raise WhatsAppError(data.get("error", {}).get("message", "Unknown error"))

                message = data["messages"][0]
                return WhatsAppMessage(id=message["id"], status="sent", recipient=to)

    async def send_template(
        self,
        to: str,
        template_name: str,
        language_code: str = "en",
        components: Optional[List[Dict]] = None,
    ) -> WhatsAppMessage:
        """Send a template message.

        Args:
            to: Recipient phone number
            template_name: Template name
            language_code: Language code (e.g., "en", "es")
            components: Template components

        """
        import aiohttp

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {"name": template_name, "language": {"code": language_code}},
        }

        if components:
            payload["template"]["components"] = components

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, json=payload, headers=headers) as response:
                data = await response.json()

                if response.status != 200:
                    raise WhatsAppError(data.get("error", {}).get("message", "Unknown error"))

                message = data["messages"][0]
                return WhatsAppMessage(id=message["id"], status="sent", recipient=to)

    async def send_image(
        self, to: str, image_url: str, caption: Optional[str] = None
    ) -> WhatsAppMessage:
        """Send an image."""
        import aiohttp

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "image",
            "image": {"link": image_url},
        }

        if caption:
            payload["image"]["caption"] = caption

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, json=payload, headers=headers) as response:
                data = await response.json()

                if response.status != 200:
                    raise WhatsAppError(data.get("error", {}).get("message", "Unknown error"))

                message = data["messages"][0]
                return WhatsAppMessage(id=message["id"], status="sent", recipient=to)

    async def send_location(
        self,
        to: str,
        latitude: float,
        longitude: float,
        name: Optional[str] = None,
        address: Optional[str] = None,
    ) -> WhatsAppMessage:
        """Send a location."""
        import aiohttp

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "location",
            "location": {"latitude": latitude, "longitude": longitude},
        }

        if name:
            payload["location"]["name"] = name
        if address:
            payload["location"]["address"] = address

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, json=payload, headers=headers) as response:
                data = await response.json()

                if response.status != 200:
                    raise WhatsAppError(data.get("error", {}).get("message", "Unknown error"))

                message = data["messages"][0]
                return WhatsAppMessage(id=message["id"], status="sent", recipient=to)

    async def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read."""
        import aiohttp

        url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"

        payload = {"messaging_product": "whatsapp", "status": "read", "message_id": message_id}

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                return response.status == 200


class WhatsAppError(Exception):
    """WhatsApp API error."""

    pass
