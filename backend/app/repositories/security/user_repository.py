"""Repository utenti."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.security.user import User


class UserRepository:
    """Repository per gli utenti applicativi."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def list_users(self) -> list[User]:
        """Restituisce gli utenti."""
        statement = select(User).order_by(User.username.asc())
        return list(self.session.scalars(statement).all())

    async def list_users_by_tenant(self, tenant_id: str) -> list[User]:
        """Restituisce gli utenti appartenenti a un tenant specifico."""
        statement = select(User).where(User.tenant_id == tenant_id).order_by(User.username.asc())
        return list(self.session.scalars(statement).all())

    async def get_user(self, user_id: str) -> User | None:
        """Restituisce un singolo utente."""
        statement = select(User).where(User.id == user_id)
        return self.session.scalar(statement)

    async def get_user_by_tenant(self, user_id: str, tenant_id: str) -> User | None:
        """Restituisce un singolo utente vincolato a uno specifico tenant."""
        statement = select(User).where(User.id == user_id, User.tenant_id == tenant_id)
        return self.session.scalar(statement)

    async def get_user_by_username(self, username: str) -> User | None:
        """Restituisce un utente tramite username."""
        statement = select(User).where(User.username == username)
        return self.session.scalar(statement)

    async def get_user_by_email(self, email: str) -> User | None:
        """Restituisce un utente tramite email."""
        statement = select(User).where(User.email == email)
        return self.session.scalar(statement)

    async def create_user(self, user: User) -> User:
        """Crea un utente."""
        self.session.add(user)
        self.session.flush()
        self.session.refresh(user)
        return user

    async def update_user(self, user: User) -> User:
        """Aggiorna un utente."""
        self.session.add(user)
        self.session.flush()
        self.session.refresh(user)
        return user
