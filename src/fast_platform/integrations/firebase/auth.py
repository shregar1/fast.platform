"""Firebase Authentication integration."""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class FirebaseUser:
    """Firebase user."""

    uid: str
    email: Optional[str] = None
    email_verified: bool = False
    display_name: Optional[str] = None
    phone_number: Optional[str] = None
    photo_url: Optional[str] = None
    disabled: bool = False
    custom_claims: Optional[Dict[str, Any]] = None


class FirebaseAuth:
    """Firebase Authentication client."""

    def __init__(self, credentials_path: Optional[str] = None):
        """Execute __init__ operation.

        Args:
            credentials_path: The credentials_path parameter.
        """
        self.credentials_path = credentials_path
        self._app = None
        self._auth = None

    def _get_auth(self):
        """Execute _get_auth operation.

        Returns:
            The result of the operation.
        """
        if self._auth is None:
            try:
                import firebase_admin
                from firebase_admin import credentials, auth

                if self.credentials_path:
                    cred = credentials.Certificate(self.credentials_path)
                    self._app = firebase_admin.initialize_app(cred)
                else:
                    # Use default app
                    self._app = firebase_admin.get_app()

                self._auth = auth

            except ImportError:
                raise ImportError("firebase-admin required for FirebaseAuth")

        return self._auth

    async def get_user(self, uid: str) -> Optional[FirebaseUser]:
        """Get user by UID."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        auth = self._get_auth()

        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                user = await loop.run_in_executor(pool, auth.get_user, uid)

            return FirebaseUser(
                uid=user.uid,
                email=user.email,
                email_verified=user.email_verified,
                display_name=user.display_name,
                phone_number=user.phone_number,
                photo_url=user.photo_url,
                disabled=user.disabled,
                custom_claims=user.custom_claims,
            )
        except Exception:
            return None

    async def get_user_by_email(self, email: str) -> Optional[FirebaseUser]:
        """Get user by email."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        auth = self._get_auth()

        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                user = await loop.run_in_executor(pool, auth.get_user_by_email, email)

            return FirebaseUser(
                uid=user.uid,
                email=user.email,
                email_verified=user.email_verified,
                display_name=user.display_name,
                phone_number=user.phone_number,
                photo_url=user.photo_url,
                disabled=user.disabled,
                custom_claims=user.custom_claims,
            )
        except Exception:
            return None

    async def create_user(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        display_name: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> FirebaseUser:
        """Create a new user."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        auth = self._get_auth()

        kwargs = {}
        if email:
            kwargs["email"] = email
        if password:
            kwargs["password"] = password
        if display_name:
            kwargs["display_name"] = display_name
        if phone_number:
            kwargs["phone_number"] = phone_number

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            user = await loop.run_in_executor(pool, lambda: auth.create_user(**kwargs))

        return FirebaseUser(
            uid=user.uid,
            email=user.email,
            display_name=user.display_name,
            phone_number=user.phone_number,
        )

    async def delete_user(self, uid: str) -> bool:
        """Delete a user."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        auth = self._get_auth()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, auth.delete_user, uid)

        return True

    async def verify_id_token(self, token: str) -> Dict[str, Any]:
        """Verify an ID token."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        auth = self._get_auth()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            decoded = await loop.run_in_executor(pool, auth.verify_id_token, token)

        return decoded

    async def set_custom_claims(self, uid: str, claims: Dict[str, Any]) -> bool:
        """Set custom claims for a user."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        auth = self._get_auth()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, auth.set_custom_user_claims, uid, claims)

        return True
