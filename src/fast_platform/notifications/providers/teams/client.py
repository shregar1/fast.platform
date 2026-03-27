"""Microsoft Teams webhook client."""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class TeamsCard:
    """Microsoft Teams adaptive card."""

    title: str
    text: Optional[str] = None
    theme_color: str = "0078D4"  # Teams blue
    sections: List[Dict[str, Any]] = field(default_factory=list)
    potential_action: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Execute to_dict operation.

        Returns:
            The result of the operation.
        """
        card = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "themeColor": self.theme_color,
            "summary": self.title,
            "title": self.title,
        }

        if self.text:
            card["text"] = self.text
        if self.sections:
            card["sections"] = self.sections
        if self.potential_action:
            card["potentialAction"] = self.potential_action

        return card


class TeamsClient:
    """Microsoft Teams webhook client."""

    def __init__(self, webhook_url: str):
        """Execute __init__ operation.

        Args:
            webhook_url: The webhook_url parameter.
        """
        self.webhook_url = webhook_url

    async def send_message(
        self, text: str, title: Optional[str] = None, theme_color: str = "0078D4"
    ) -> bool:
        """Send a simple text message."""
        import aiohttp

        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "themeColor": theme_color,
            "text": text,
        }

        if title:
            payload["title"] = title

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.webhook_url, json=payload, headers={"Content-Type": "application/json"}
            ) as response:
                return response.status == 200

    async def send_card(self, card: TeamsCard) -> bool:
        """Send an adaptive card."""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.webhook_url, json=card.to_dict(), headers={"Content-Type": "application/json"}
            ) as response:
                return response.status == 200

    async def send_mention(self, text: str, mentioned_email: str, mentioned_name: str) -> bool:
        """Send message with user mention."""
        import aiohttp

        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "text": f"<at>{mentioned_name}</at> {text}",
            "entities": [
                {
                    "type": "mention",
                    "text": f"<at>{mentioned_name}</at>",
                    "mentioned": {"id": mentioned_email, "name": mentioned_name},
                }
            ],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.webhook_url, json=payload, headers={"Content-Type": "application/json"}
            ) as response:
                return response.status == 200

    async def send_alert(
        self,
        title: str,
        description: str,
        severity: str = "info",  # info, warning, error
        facts: Optional[List[Dict[str, str]]] = None,
    ) -> bool:
        """Send an alert card."""
        colors = {"info": "0078D4", "warning": "FFC107", "error": "F44336", "success": "28A745"}

        section = {"activityTitle": title, "activitySubtitle": description, "markdown": True}

        if facts:
            section["facts"] = [{"name": k, "value": v} for k, v in facts]

        card = TeamsCard(
            title=title, theme_color=colors.get(severity, "0078D4"), sections=[section]
        )

        return await self.send_card(card)
