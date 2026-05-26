"""Modello ORM dell'utente."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDStr


class User(Base):
    """Utente applicativo."""

    __tablename__ = "users"
    __table_args__ = {"schema": "security"}

    id: Mapped[str] = mapped_column(UUIDStr(), primary_key=True, default=lambda: str(uuid4()))
    username: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role_code: Mapped[str] = mapped_column(
        ForeignKey("security.roles.code"),
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    person_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    tenant_id: Mapped[str | None] = mapped_column(
        UUIDStr(),
        ForeignKey("security.tenants.id"),
        nullable=True,
        index=True,
    )
    legacy_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
