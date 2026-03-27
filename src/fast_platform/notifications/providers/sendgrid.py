"""
SendGrid email integration
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class EmailAttachment:
    """Email attachment"""
    filename: str
    content: bytes
    content_type: str = "application/octet-stream"


@dataclass
class EmailMessage:
    """Email message"""
    to: List[str]
    subject: str
    body: Optional[str] = None
    html_body: Optional[str] = None
    from_email: Optional[str] = None
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    attachments: List[EmailAttachment] = field(default_factory=list)


@dataclass
class EmailResult:
    """Email send result"""
    message_id: str
    status: str


class SendGridClient:
    """
    SendGrid email client
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None
    ):
        self.api_key = api_key
        self.from_email = from_email
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                from sendgrid import SendGridAPIClient
                self._client = SendGridAPIClient(api_key=self.api_key)
            except ImportError:
                raise ImportError("sendgrid package required for SendGridClient")
        return self._client
    
    async def send_email(self, message: EmailMessage) -> EmailResult:
        """
        Send an email
        
        Args:
            message: Email message to send
        """
        from sendgrid.helpers.mail import (
            Mail, Email, To, Content, Attachment, FileContent,
            FileName, FileType, Disposition
        )
        import base64
        
        from_email = message.from_email or self.from_email
        if not from_email:
            raise ValueError("from_email required")
        
        mail = Mail(
            from_email=Email(from_email),
            to_emails=[To(addr) for addr in message.to],
            subject=message.subject
        )
        
        if message.body:
            mail.add_content(Content("text/plain", message.body))
        if message.html_body:
            mail.add_content(Content("text/html", message.html_body))
        
        # Add CC and BCC
        for cc in message.cc:
            mail.add_cc(Email(cc))
        for bcc in message.bcc:
            mail.add_bcc(Email(bcc))
        
        # Add attachments
        for att in message.attachments:
            encoded = base64.b64encode(att.content).decode()
            attachment = Attachment()
            attachment.file_content = FileContent(encoded)
            attachment.file_name = FileName(att.filename)
            attachment.file_type = FileType(att.content_type)
            attachment.disposition = Disposition("attachment")
            mail.add_attachment(attachment)
        
        client = self._get_client()
        response = client.send(mail)
        
        return EmailResult(
            message_id=response.headers.get("X-Message-Id", ""),
            status="sent" if response.status_code == 202 else "failed"
        )
    
    async def send_template_email(
        self,
        to: List[str],
        template_id: str,
        template_data: Dict[str, Any],
        from_email: Optional[str] = None
    ) -> EmailResult:
        """Send an email using a template"""
        from sendgrid.helpers.mail import Mail, Email, To
        
        from_addr = from_email or self.from_email
        
        mail = Mail(
            from_email=Email(from_addr),
            to_emails=[To(addr) for addr in to]
        )
        mail.template_id = template_id
        mail.dynamic_template_data = template_data
        
        client = self._get_client()
        response = client.send(mail)
        
        return EmailResult(
            message_id=response.headers.get("X-Message-Id", ""),
            status="sent" if response.status_code == 202 else "failed"
        )
