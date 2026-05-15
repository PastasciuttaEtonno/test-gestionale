"""Utility per la gestione dei token JWT."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt
from jwt import InvalidTokenError as JwtInvalidTokenError

from app.core.config import settings
from app.domain.security.exceptions import InvalidTokenError


class JwtTokenManager:
    """Gestore dei token JWT."""

    def create_access_token(self, subject: str, claims: dict[str, Any]) -> str:
        """Crea un access token."""
        expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
        payload = {
            "sub": subject,
            "type": "access",
            "iss": settings.jwt_issuer,
            "exp": expires_at,
            **claims,
        }
        return jwt.encode(
            payload=payload,
            key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

    def create_refresh_token(
        self,
        subject: str,
        claims: dict[str, Any],
    ) -> tuple[str, str, datetime]:
        """Crea un refresh token."""
        token_identifier = str(uuid4())
        expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
        payload = {
            "sub": subject,
            "type": "refresh",
            "iss": settings.jwt_issuer,
            "jti": token_identifier,
            "exp": expires_at,
            **claims,
        }
        token = jwt.encode(
            payload=payload,
            key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
        return token, token_identifier, expires_at

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decodifica un token JWT."""
        try:
            return jwt.decode(
                jwt=token,
                key=settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
                issuer=settings.jwt_issuer,
            )
        except JwtInvalidTokenError as exc:
            raise InvalidTokenError("Token non valido o scaduto.") from exc
