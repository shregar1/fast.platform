"""Email service configuration DTO."""

from __future__ import annotations

from typing import Literal, Optional

from .abstraction import IDTO


class SMTPConfigDTO(IDTO):
    """SMTP server configuration."""

    host: str = "localhost"
    port: int = 587
    user_name: str = ""
    password: str = ""
    use_tls: bool = True
    use_ssl: bool = False
    timeout_seconds: float = 10.0


class SESConfigDTO(IDTO):
    """AWS SES configuration."""

    region: str = "us-east-1"
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    configuration_set: Optional[str] = None


class SendGridConfigDTO(IDTO):
    """SendGrid API configuration."""

    api_key: Optional[str] = None


class MailgunConfigDTO(IDTO):
    """Mailgun API configuration."""

    api_key: Optional[str] = None
    domain: Optional[str] = None
    region: Literal["us", "eu"] = "us"


class EmailConfigurationDTO(IDTO):
    """Global email configuration supporting multiple providers."""

    provider: Literal["smtp", "ses", "sendgrid", "mailgun"] = "smtp"
    default_from_email: str = "noreply@example.com"
    default_from_name: str = "FastMVC"
    
    smtp: SMTPConfigDTO = SMTPConfigDTO()
    ses: SESConfigDTO = SESConfigDTO()
    sendgrid: SendGridConfigDTO = SendGridConfigDTO()
    mailgun: MailgunConfigDTO = MailgunConfigDTO()
