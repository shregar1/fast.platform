"""Fast Platform Notifications.

Unified notification system supporting 12+ channels:

**Email:**
- SendGrid - Transactional emails
- Amazon SES - Scalable email service
- Mailgun - Developer-friendly email API

**SMS:**
- Twilio - Global SMS delivery

**Chat:**
- Slack - Team messaging
- Discord - Community chat
- Telegram - Bot messaging
- Microsoft Teams - Enterprise chat

**Push:**
- OneSignal - Cross-platform push

**Real-time:**
- Pusher - WebSocket notifications
- Webhooks - Generic HTTP callbacks

**Firebase:**
- FCM - Firebase Cloud Messaging

Usage:
    from fast_platform.notifications import (
        SendGridClient,
        TwilioClient,
        SlackClient
    )

    email = SendGridClient(api_key="...")
    await email.send_email(to="user@example.com", subject="Hello")
"""

# Import all providers from the providers module
from .providers.slack import SlackClient, SlackBlock
from .providers.twilio import TwilioClient
from .providers.sendgrid import SendGridClient
from .providers.discord import DiscordClient, DiscordEmbed
from .providers.telegram import TelegramClient
from .providers.teams import TeamsClient, TeamsCard
from .providers.webhook import WebhookClient, WebhookSignature
from .providers.ses import SESClient
from .providers.mailgun import MailgunClient
from .providers.pusher import PusherClient, PusherChannel
from .providers.onesignal import OneSignalClient, OneSignalNotification, DeviceType

__all__ = [
    # Email providers
    "SendGridClient",
    "SESClient",
    "MailgunClient",
    # SMS providers
    "TwilioClient",
    # Chat providers
    "SlackClient",
    "SlackBlock",
    "DiscordClient",
    "DiscordEmbed",
    "TelegramClient",
    "TeamsClient",
    "TeamsCard",
    # Push providers
    "OneSignalClient",
    "OneSignalNotification",
    "DeviceType",
    # Real-time
    "PusherClient",
    "PusherChannel",
    # Webhooks
    "WebhookClient",
    "WebhookSignature",
]
