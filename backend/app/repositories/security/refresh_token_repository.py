"""Repository refresh token."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.security.refresh_token import RefreshToken


class RefreshTokenRepository:
    """Repository per le sessioni refresh token."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def persist(self, refresh_token: RefreshToken) -> RefreshToken:
        """Salva un record di refresh token."""
        self.session.add(refresh_token)
        self.session.flush()
        self.session.refresh(refresh_token)
        return refresh_token

    async def get_active_by_identifier(self, token_identifier: str) -> RefreshToken | None:
        """Restituisce un refresh token attivo tramite identificatore."""
        statement = select(RefreshToken).where(
            RefreshToken.token_identifier == token_identifier,
            RefreshToken.revoked_at.is_(None),
        )
        return self.session.scalar(statement)

    async def revoke(self, token_identifier: str, revoked_reason: str) -> None:
        """Revoca un refresh token."""
        token = await self.get_active_by_identifier(token_identifier)
        if token is None:
            return
        token.revoked_at = datetime.utcnow()
        token.revoked_reason = revoked_reason
        self.session.add(token)
        self.session.flush()

    async def revoke_all_for_user(self, user_id: str, revoked_reason: str) -> int:
        """Revoca tutti i refresh token attivi di un utente."""
        statement = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
        tokens = list(self.session.scalars(statement).all())
        for token in tokens:
            token.revoked_at = datetime.utcnow()
            token.revoked_reason = revoked_reason
            self.session.add(token)
        self.session.flush()
        return len(tokens)
