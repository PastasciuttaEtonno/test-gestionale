"""Modello ORM del refresh token."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDStr


class RefreshToken(Base):
    """Record di sessione associato a refresh token."""

    __tablename__ = "refresh_tokens"
    __table_args__ = {"schema": "security"}

    id: Mapped[str] = mapped_column(UUIDStr(), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(UUIDStr(), ForeignKey("security.users.id"), index=True)
    token_identifier: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    family_id: Mapped[str] = mapped_column(UUIDStr(), index=True)
    parent_token_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    family_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
