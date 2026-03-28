"""JWT Utility Implementation for FastPlatform.

Provides standard JWT operations (encode, decode) follow the IUtility abstraction.
"""

from __future__ import annotations

import jwt
from typing import Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from .abstraction import IUtility


class JWTUtility(IUtility):
    """Concrete implementation of JWT operations.
    
    This utility wraps the PyJWT library to provide a consistent interface for
    encoding and decoding tokens across the monorepo.
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        urn: Optional[str] = None,
        user_urn: Optional[str] = None,
        api_name: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """Initialize with configuration and optional request context.
        
        Args:
            secret_key: The secret key used for signing/verification.
            algorithm: The signing algorithm to use (default: HS256).
            urn: Optional request identifier for contextual logging.
            user_urn: Optional user identifier.
            api_name: Optional name of the API being called.
            user_id: Optional user ID.
        """
        self.secret = secret_key
        self.algorithm = algorithm
        self.urn = urn
        self.user_urn = user_urn
        self.api_name = api_name
        self.user_id = user_id

    def encode_token(self, payload: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Encode a payload into a JWT token.
        
        Args:
            payload: The dictionary to encode.
            expires_delta: Optional expiration time (defaults to 15 minutes).
            
        Returns:
            str: The encoded JWT string.
        """
        to_encode = payload.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and validate a JWT token.
        
        Args:
            token: The JWT string to decode.
            
        Returns:
            dict: The decoded payload.
            
        Raises:
            ValueError: If the token is expired or invalid.
        """
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired", urn=self.urn)
            raise ValueError("Token expired")
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}", urn=self.urn)
            raise ValueError("Invalid token")
