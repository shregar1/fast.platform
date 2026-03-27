"""Slack integration."""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class SlackBlock:
    """Slack block."""

    type: str
    text: Optional[Dict[str, str]] = None
    fields: Optional[List[Dict]] = None
    accessory: Optional[Dict] = None


class SlackClient:
    """Slack API client."""

    def __init__(self, bot_token: Optional[str] = None, webhook_url: Optional[str] = None):
        """Execute __init__ operation.

        Args:
            bot_token: The bot_token parameter.
            webhook_url: The webhook_url parameter.
        """
        self.bot_token = bot_token
        self.webhook_url = webhook_url
        self._client = None

    def _get_client(self):
        """Execute _get_client operation.

        Returns:
            The result of the operation.
        """
        if self._client is None:
            try:
                from slack_sdk import WebClient

                self._client = WebClient(token=self.bot_token)
            except ImportError:
                raise ImportError("slack_sdk package required for SlackClient")
        return self._client

    async def post_message(
        self,
        channel: str,
        text: str,
        blocks: Optional[List[SlackBlock]] = None,
        thread_ts: Optional[str] = None,
        unfurl_links: bool = True,
    ) -> Dict[str, Any]:
        """Post a message to a channel.

        Args:
            channel: Channel ID or name
            text: Message text
            blocks: Optional rich blocks
            thread_ts: Optional thread timestamp

        """
        client = self._get_client()

        params = {"channel": channel, "text": text, "unfurl_links": unfurl_links}

        if blocks:
            params["blocks"] = [
                {
                    "type": b.type,
                    **{
                        k: v
                        for k, v in {
                            "text": b.text,
                            "fields": b.fields,
                            "accessory": b.accessory,
                        }.items()
                        if v is not None
                    },
                }
                for b in blocks
            ]

        if thread_ts:
            params["thread_ts"] = thread_ts

        return client.chat_postMessage(**params)

    async def send_webhook(
        self,
        text: str,
        blocks: Optional[List[SlackBlock]] = None,
        webhook_url: Optional[str] = None,
    ) -> bool:
        """Send message via webhook.

        Args:
            text: Message text
            blocks: Optional rich blocks
            webhook_url: Optional webhook URL (uses default if not provided)

        """
        import aiohttp

        url = webhook_url or self.webhook_url
        if not url:
            raise ValueError("webhook_url required")

        payload = {"text": text}
        if blocks:
            payload["blocks"] = [
                {
                    "type": b.type,
                    **{
                        k: v
                        for k, v in {"text": b.text, "fields": b.fields}.items()
                        if v is not None
                    },
                }
                for b in blocks
            ]

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                return response.status == 200

    async def upload_file(
        self, channel: str, file_content: bytes, filename: str, title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload a file to a channel."""
        client = self._get_client()

        from io import BytesIO

        return client.files_upload_v2(
            channel=channel, file=BytesIO(file_content), filename=filename, title=title or filename
        )
