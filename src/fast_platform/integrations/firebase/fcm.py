"""Firebase Cloud Messaging (FCM) integration."""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class PushNotification:
    """Push notification payload."""

    title: str
    body: str
    data: Optional[Dict[str, str]] = None
    image_url: Optional[str] = None
    sound: str = "default"
    badge: Optional[int] = None
    priority: str = "high"  # high or normal

    def to_fcm_payload(self, token: str) -> Dict[str, Any]:
        """Convert to FCM message format."""
        message = {
            "token": token,
            "notification": {"title": self.title, "body": self.body},
            "android": {"priority": self.priority, "notification": {"sound": self.sound}},
            "apns": {"payload": {"aps": {"sound": self.sound, "badge": self.badge}}},
        }

        if self.data:
            message["data"] = self.data

        if self.image_url:
            message["notification"]["image"] = self.image_url

        return {"message": message}


class FCMClient:
    """Firebase Cloud Messaging client."""

    def __init__(self, credentials_path: Optional[str] = None, project_id: Optional[str] = None):
        """Execute __init__ operation.

        Args:
            credentials_path: The credentials_path parameter.
            project_id: The project_id parameter.
        """
        self.credentials_path = credentials_path
        self.project_id = project_id
        self._client = None
        self._base_url = None

    def _get_client(self):
        """Execute _get_client operation.

        Returns:
            The result of the operation.
        """
        if self._client is None:
            try:
                from google.oauth2 import service_account
                import google.auth.transport.requests

                if self.credentials_path:
                    credentials = service_account.Credentials.from_service_account_file(
                        self.credentials_path,
                        scopes=["https://www.googleapis.com/auth/cloud-platform"],
                    )
                else:
                    # Use default credentials
                    import google.auth

                    credentials, self.project_id = google.auth.default(
                        scopes=["https://www.googleapis.com/auth/cloud-platform"]
                    )

                self._client = google.auth.transport.requests.AuthorizedSession(credentials)
                self._base_url = (
                    f"https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send"
                )

            except ImportError:
                raise ImportError("google-auth required for FCMClient")

        return self._client

    async def send_to_token(self, token: str, notification: PushNotification) -> Dict[str, Any]:
        """Send push notification to a single device.

        Args:
            token: FCM device token
            notification: Notification payload

        """
        import aiohttp

        client = self._get_client()
        payload = notification.to_fcm_payload(token)

        # For async, we need to use the credentials to get a token
        # and then make an aiohttp request
        import google.auth.transport.requests

        request = google.auth.transport.requests.Request()
        client.credentials.refresh(request)

        headers = {
            "Authorization": f"Bearer {client.credentials.token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self._base_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    raise FCMError(f"FCM request failed: {error}")

    async def send_to_tokens(
        self, tokens: List[str], notification: PushNotification
    ) -> List[Dict[str, Any]]:
        """Send to multiple devices."""
        results = []
        for token in tokens:
            try:
                result = await self.send_to_token(token, notification)
                results.append({"token": token, "success": True, "result": result})
            except Exception as e:
                results.append({"token": token, "success": False, "error": str(e)})
        return results

    async def send_to_topic(self, topic: str, notification: PushNotification) -> Dict[str, Any]:
        """Send to a topic."""
        # Modify payload to use topic instead of token
        payload = notification.to_fcm_payload("")
        payload["message"]["topic"] = topic
        del payload["message"]["token"]

        import aiohttp
        from google.auth.transport.requests import Request

        client = self._get_client()
        request = Request()
        client.credentials.refresh(request)

        headers = {
            "Authorization": f"Bearer {client.credentials.token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self._base_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    raise FCMError(f"FCM request failed: {error}")

    async def subscribe_to_topic(self, tokens: List[str], topic: str) -> Dict[str, Any]:
        """Subscribe tokens to a topic."""
        import aiohttp
        from google.auth.transport.requests import Request

        client = self._get_client()
        request = Request()
        client.credentials.refresh(request)

        url = f"https://iid.googleapis.com/iid/v1:batchAdd"

        headers = {
            "Authorization": f"Bearer {client.credentials.token}",
            "Content-Type": "application/json",
        }

        payload = {"to": f"/topics/{topic}", "registration_tokens": tokens}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                return await response.json()


class FCMError(Exception):
    """FCM error."""

    pass
