"""Mailgun email provider client."""

from typing import Any


class MailgunClient:
    """Mailgun API client for sending emails."""

    def __init__(self, api_key: str, domain: str, region: str = "us"):
        """Initialize Mailgun client.
        
        Args:
            api_key: Mailgun API key
            domain: Mailgun domain
            region: Region (us or eu)
        """
        self.api_key = api_key
        self.domain = domain
        self.region = region
        self.base_url = (
            "https://api.eu.mailgun.net/v3" if region == "eu" else "https://api.mailgun.net/v3"
        )

    async def send_email(
        self,
        to: list[str],
        subject: str,
        text: str | None = None,
        html: str | None = None,
        from_email: str | None = None,
    ) -> dict[str, Any]:
        """Send email via Mailgun."""
        raise NotImplementedError("Install aiohttp to use MailgunClient")

    async def send_template(
        self,
        to: list[str],
        template: str,
        subject: str,
        template_vars: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send templated email."""
        raise NotImplementedError("Install aiohttp to use MailgunClient")

    async def create_template(
        self, name: str, description: str, template: str
    ) -> bool:
        """Create email template."""
        raise NotImplementedError("Install aiohttp to use MailgunClient")

    async def get_events(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get Mailgun events."""
        raise NotImplementedError("Install aiohttp to use MailgunClient")

    async def validate_email(self, email: str) -> dict[str, Any]:
        """Validate email address."""
        raise NotImplementedError("Install aiohttp to use MailgunClient")


__all__ = ["MailgunClient"]
