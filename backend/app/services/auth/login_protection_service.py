"""Servizio applicativo per rate limiting e cooldown del login."""

from datetime import UTC, datetime, timedelta

from app.core.config import settings
from app.models.security.login_protection import LoginProtection
from app.repositories.security.login_protection_repository import LoginProtectionRepository


class LoginProtectionService:
    """Gestisce tentativi falliti, finestre temporali e lockout del login."""

    def __init__(self, repository: LoginProtectionRepository) -> None:
        self.repository = repository

    async def get_lock_state(self, identifier: str, ip_address: str) -> LoginProtection | None:
        """Restituisce lo stato corrente della coppia identificativo e IP."""
        return await self.repository.get_entry(identifier=identifier, ip_address=ip_address)

    async def is_locked(self, identifier: str, ip_address: str) -> bool:
        """Indica se la coppia identificativo e IP e attualmente bloccata."""
        entry = await self.get_lock_state(identifier=identifier, ip_address=ip_address)
        if entry is None or entry.locked_until is None:
            return False
        return entry.locked_until > datetime.now(UTC)

    async def register_failed_attempt(self, identifier: str, ip_address: str) -> LoginProtection:
        """Registra un tentativo fallito e applica lockout se necessario."""
        now = datetime.now(UTC)
        entry = await self.get_lock_state(identifier=identifier, ip_address=ip_address)
        if entry is None:
            entry = LoginProtection(
                identifier=identifier,
                ip_address=ip_address,
                failed_count=1,
                window_started_at=now,
                last_failed_at=now,
                locked_until=None,
            )
            return await self.repository.save(entry)

        if now - entry.window_started_at > timedelta(
            minutes=settings.login_rate_limit_window_minutes
        ):
            entry.failed_count = 1
            entry.window_started_at = now
            entry.locked_until = None
        else:
            entry.failed_count += 1

        entry.last_failed_at = now
        if entry.failed_count >= settings.login_rate_limit_max_attempts:
            entry.locked_until = now + timedelta(minutes=settings.login_rate_limit_lockout_minutes)
        return await self.repository.save(entry)

    async def clear_state(self, identifier: str, ip_address: str) -> None:
        """Azzera lo stato di protezione login dopo autenticazione riuscita."""
        entry = await self.get_lock_state(identifier=identifier, ip_address=ip_address)
        if entry is None:
            return
        now = datetime.now(UTC)
        entry.failed_count = 0
        entry.window_started_at = now
        entry.last_failed_at = None
        entry.locked_until = None
        await self.repository.save(entry)
