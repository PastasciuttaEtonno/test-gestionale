"""Repository per la protezione del login."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.security.login_protection import LoginProtection


class LoginProtectionRepository:
    """Repository dello stato di rate limiting e lockout login."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def get_entry(self, identifier: str, ip_address: str) -> LoginProtection | None:
        """Restituisce lo stato associato alla coppia identificativo e IP."""
        statement = select(LoginProtection).where(
            LoginProtection.identifier == identifier,
            LoginProtection.ip_address == ip_address,
        )
        return self.session.scalar(statement)

    async def save(self, entry: LoginProtection) -> LoginProtection:
        """Salva o aggiorna lo stato di protezione login."""
        self.session.add(entry)
        self.session.flush()
        self.session.refresh(entry)
        return entry
