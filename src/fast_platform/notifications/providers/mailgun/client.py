"""Mailgun API client."""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class MailgunAttachment:
    """Mailgun email attachment."""

    filename: str
    content: bytes
    content_type: Optional[str] = None


class MailgunClient:
    """Mailgun API client."""

    def __init__(
        self,
        api_key: str,
        domain: str,
        region: str = "us",  # us or eu
    ):
        """Execute __init__ operation.

        Args:
            api_key: The api_key parameter.
            domain: The domain parameter.
            region: The region parameter.
        """
        self.api_key = api_key
        self.domain = domain
        self.region = region
        self.base_url = f"https://api.{region}.mailgun.net/v3"

    async def send_email(
        self,
        to: List[str],
        subject: str,
        text: Optional[str] = None,
        html: Optional[str] = None,
        from_email: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
        attachments: Optional[List[MailgunAttachment]] = None,
        tags: Optional[List[str]] = None,
        tracking: bool = True,
    ) -> Dict[str, Any]:
        """Send an email via Mailgun.

        Args:
            to: Recipients
            subject: Email subject
            text: Plain text body
            html: HTML body
            from_email: Sender (defaults to domain)
            attachments: File attachments
            tags: Message tags
            tracking: Enable open/click tracking

        """
        import aiohttp
        import base64

        url = f"{self.base_url}/{self.domain}/messages"

        auth = aiohttp.BasicAuth("api", self.api_key)

        data = {"to": ",".join(to), "subject": subject, "o:tracking": str(tracking).lower()}

        if from_email:
            data["from"] = from_email
        else:
            data["from"] = f"noreply@{self.domain}"

        if text:
            data["text"] = text
        if html:
            data["html"] = html
        if cc:
            data["cc"] = ",".join(cc)
        if bcc:
            data["bcc"] = ",".join(bcc)
        if reply_to:
            data["h:Reply-To"] = reply_to
        if tags:
            for i, tag in enumerate(tags[:3]):  # Max 3 tags
                data[f"o:tag[{i}]"] = tag

        # Handle attachments
        files = []
        if attachments:
            for att in attachments:
                files.append(
                    (
                        "attachment",
                        (att.filename, att.content, att.content_type or "application/octet-stream"),
                    )
                )

        async with aiohttp.ClientSession() as session:
            if files:
                data_sent = aiohttp.FormData()
                for key, value in data.items():
                    data_sent.add_field(key, value)
                for name, file_info in files:
                    data_sent.add_field(
                        name, file_info[1], filename=file_info[0], content_type=file_info[2]
                    )

                async with session.post(url, data=data_sent, auth=auth) as response:
                    return await response.json()
            else:
                async with session.post(url, data=data, auth=auth) as response:
                    return await response.json()

    async def send_template(
        self,
        to: List[str],
        template: str,
        subject: str,
        template_vars: Optional[Dict[str, Any]] = None,
        from_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send using a Mailgun template."""
        import aiohttp

        url = f"{self.base_url}/{self.domain}/messages"

        auth = aiohttp.BasicAuth("api", self.api_key)

        data = {"to": ",".join(to), "subject": subject, "template": template}

        if from_email:
            data["from"] = from_email
        else:
            data["from"] = f"noreply@{self.domain}"

        if template_vars:
            for key, value in template_vars.items():
                data[f"v:{key}"] = str(value)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, auth=auth) as response:
                return await response.json()

    async def create_template(
        self,
        name: str,
        description: str,
        template: str,  # HTML template with {{variables}}
    ) -> bool:
        """Create or update a template."""
        import aiohttp

        url = f"{self.base_url}/{self.domain}/templates"

        auth = aiohttp.BasicAuth("api", self.api_key)

        data = {"name": name, "description": description, "template": template}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, auth=auth) as response:
                return response.status == 200

    async def get_events(
        self,
        begin: Optional[str] = None,
        end: Optional[str] = None,
        ascending: bool = False,
        limit: int = 300,
    ) -> List[Dict[str, Any]]:
        """Get event log."""
        import aiohttp

        url = f"{self.base_url}/{self.domain}/events"

        auth = aiohttp.BasicAuth("api", self.api_key)

        params = {"ascending": str(ascending).lower(), "limit": limit}

        if begin:
            params["begin"] = begin
        if end:
            params["end"] = end

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, auth=auth) as response:
                data = await response.json()
                return data.get("items", [])

    async def validate_email(self, address: str) -> Dict[str, Any]:
        """Validate an email address."""
        import aiohttp

        url = f"{self.base_url}/address/validate"

        auth = aiohttp.BasicAuth("api", self.api_key)

        params = {"address": address}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, auth=auth) as response:
                return await response.json()
