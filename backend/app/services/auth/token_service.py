"""Servizio segnaposto per la gestione dei token."""


class TokenService:
    """Servizio applicativo per il ciclo di vita dei token."""

    async def issue_tokens(self, user_id: str) -> dict:
        """Emette access token e refresh token."""
        raise NotImplementedError

    async def rotate_refresh_token(self, refresh_token: str) -> dict:
        """Ruota un refresh token."""
        raise NotImplementedError
