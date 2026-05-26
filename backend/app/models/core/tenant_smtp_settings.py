"""Modello ORM delle impostazioni SMTP del tenant."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDStr


class TenantSmtpSettings(Base):
    """Configurazione SMTP usata dall'azienda cliente per l'invio email."""

    __tablename__ = "tenant_smtp_settings"
    __table_args__ = {"schema": "core"}

    tenant_id: Mapped[str] = mapped_column(
        UUIDStr(),
        ForeignKey("security.tenants.id"),
        primary_key=True,
    )
    host: Mapped[str] = mapped_column(String(255))
    port: Mapped[int] = mapped_column(Integer)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_encrypted: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    sender_email: Mapped[str] = mapped_column(String(255))
    sender_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    use_tls: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
