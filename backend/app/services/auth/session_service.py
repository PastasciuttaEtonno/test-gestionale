"""Servizio segnaposto per la gestione sessioni."""


class SessionService:
    """Servizio applicativo per persistenza e revoca delle sessioni."""

    async def create_session(self, user_id: str, metadata: dict | None = None) -> None:
        """Persiste una sessione."""
        raise NotImplementedError

    async def revoke_session(self, token_identifier: str) -> None:
        """Revoca una sessione."""
        raise NotImplementedError
