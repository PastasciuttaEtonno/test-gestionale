"""Modello ORM per rate limiting e lockout del login."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LoginProtection(Base):
    """Stato di protezione login per coppia identificativo e indirizzo IP."""

    __tablename__ = "login_protection"
    __table_args__ = (
        UniqueConstraint("identifier", "ip_address", name="uq_login_protection_identifier_ip"),
        {"schema": "security"},
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    identifier: Mapped[str] = mapped_column(String(255), index=True)
    ip_address: Mapped[str] = mapped_column(String(64), index=True)
    failed_count: Mapped[int] = mapped_column(default=0)
    window_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
