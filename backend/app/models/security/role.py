"""Modello ORM del ruolo."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Role(Base):
    """Ruolo di sicurezza."""

    __tablename__ = "roles"
    __table_args__ = {"schema": "security"}

    code: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
