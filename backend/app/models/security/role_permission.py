"""Modello ORM di associazione ruolo-permesso."""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RolePermission(Base):
    """Associazione tra ruolo e permesso."""

    __tablename__ = "role_permissions"
    __table_args__ = {"schema": "security"}

    role_code: Mapped[str] = mapped_column(
        ForeignKey("security.roles.code"),
        primary_key=True,
    )
    permission_code: Mapped[str] = mapped_column(
        ForeignKey("security.permissions.code"),
        primary_key=True,
    )
