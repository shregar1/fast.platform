"""AWS SES email provider client."""

from typing import Any


class SESClient:
    """AWS SES client for sending emails."""

    def __init__(
        self,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        region_name: str = "us-east-1",
    ):
        """Initialize SES client.
        
        Args:
            aws_access_key_id: AWS access key
            aws_secret_access_key: AWS secret key
            region_name: AWS region
        """
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name

    async def send_email(
        self,
        to: list[str],
        subject: str,
        text: str | None = None,
        html: str | None = None,
        from_email: str | None = None,
    ) -> dict[str, Any]:
        """Send email via SES."""
        raise NotImplementedError("Install boto3 to use SESClient")

    async def send_template(
        self,
        to: list[str],
        template: str,
        subject: str,
        template_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send templated email."""
        raise NotImplementedError("Install boto3 to use SESClient")

    async def create_template(
        self, name: str, subject: str, html: str, text: str
    ) -> bool:
        """Create email template."""
        raise NotImplementedError("Install boto3 to use SESClient")


__all__ = ["SESClient"]
