"""Repository ruoli e permessi."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.security.permission import Permission
from app.models.security.role import Role
from app.models.security.role_permission import RolePermission


class RoleRepository:
    """Repository per ruoli e permessi."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def get_role(self, role_code: str) -> Role | None:
        """Restituisce un singolo ruolo."""
        statement = select(Role).where(Role.code == role_code)
        return self.session.scalar(statement)

    async def list_permissions_by_role(self, role_code: str) -> list[str]:
        """Restituisce i permessi associati a un ruolo."""
        statement = (
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_code == Permission.code)
            .where(RolePermission.role_code == role_code)
            .order_by(Permission.code.asc())
        )
        return list(self.session.scalars(statement).all())
