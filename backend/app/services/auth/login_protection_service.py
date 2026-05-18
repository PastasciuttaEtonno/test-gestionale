"""Servizio applicativo per rate limiting e cooldown del login."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.core.config import settings
from app.models.security.login_protection import LoginProtection
from app.repositories.security.login_protection_repository import LoginProtectionRepository

ACCOUNT_SCOPE_IP = "__scope_identifier__"
IP_SCOPE_IDENTIFIER = "__scope_ip__"


@dataclass(slots=True)
class LoginProtectionResult:
    """Esito aggregato della protezione login."""

    failed_count: int
    locked_until: datetime | None
    active_scopes: list[str]


class LoginProtectionService:
    """Gestisce tentativi falliti, finestre temporali e lockout del login."""

    def __init__(self, repository: LoginProtectionRepository) -> None:
        self.repository = repository

    async def get_lock_state(self, identifier: str, ip_address: str) -> LoginProtection | None:
        """Restituisce lo stato corrente della coppia identificativo e IP."""
        return await self.repository.get_entry(identifier=identifier, ip_address=ip_address)

    async def is_locked(self, identifier: str, ip_address: str) -> bool:
        """Indica se almeno uno scope di protezione login e attualmente bloccato."""
        return (await self.get_lock_result(identifier, ip_address)).locked_until is not None

    async def get_lock_result(self, identifier: str, ip_address: str) -> LoginProtectionResult:
        """Restituisce lo stato aggregato di blocco per account, IP e coppia esatta."""
        now = datetime.now(UTC)
        active_scopes: list[str] = []
        locked_until_candidates: list[datetime] = []
        max_failed_count = 0

        for scope_name, scope_identifier, scope_ip in self._iter_scope_keys(identifier, ip_address):
            entry = await self.get_lock_state(identifier=scope_identifier, ip_address=scope_ip)
            if entry is None:
                continue
            max_failed_count = max(max_failed_count, entry.failed_count)
            if entry.locked_until is not None and entry.locked_until > now:
                active_scopes.append(scope_name)
                locked_until_candidates.append(entry.locked_until)

        return LoginProtectionResult(
            failed_count=max_failed_count,
            locked_until=max(locked_until_candidates) if locked_until_candidates else None,
            active_scopes=active_scopes,
        )

    async def register_failed_attempt(
        self,
        identifier: str,
        ip_address: str,
    ) -> LoginProtectionResult:
        """Registra un tentativo fallito su tutti gli scope di protezione login."""
        results = []
        for scope_name, scope_identifier, scope_ip in self._iter_scope_keys(identifier, ip_address):
            entry = await self._register_failed_attempt_for_key(
                identifier=scope_identifier,
                ip_address=scope_ip,
                max_attempts=self._max_attempts_for_scope(scope_name),
            )
            results.append((scope_name, entry))

        locked_entries = [
            (scope_name, entry)
            for scope_name, entry in results
            if entry.locked_until is not None and entry.locked_until > datetime.now(UTC)
        ]
        max_failed_count = max(entry.failed_count for _, entry in results)
        locked_until = max((entry.locked_until for _, entry in locked_entries), default=None)
        active_scopes = [scope_name for scope_name, _ in locked_entries]
        return LoginProtectionResult(
            failed_count=max_failed_count,
            locked_until=locked_until,
            active_scopes=active_scopes,
        )

    async def _register_failed_attempt_for_key(
        self,
        identifier: str,
        ip_address: str,
        max_attempts: int,
    ) -> LoginProtection:
        """Registra un tentativo fallito per una specifica chiave di protezione."""
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
        if entry.failed_count >= max_attempts:
            entry.locked_until = now + timedelta(minutes=settings.login_rate_limit_lockout_minutes)
        return await self.repository.save(entry)

    async def clear_state(self, identifier: str, ip_address: str) -> None:
        """Azzera lo stato di protezione login dopo autenticazione riuscita."""
        for _, scope_identifier, scope_ip in self._iter_scope_keys(identifier, ip_address):
            entry = await self.get_lock_state(identifier=scope_identifier, ip_address=scope_ip)
            if entry is None:
                continue
            now = datetime.now(UTC)
            entry.failed_count = 0
            entry.window_started_at = now
            entry.last_failed_at = None
            entry.locked_until = None
            await self.repository.save(entry)

    def _iter_scope_keys(
        self,
        identifier: str,
        ip_address: str,
    ) -> tuple[tuple[str, str, str], ...]:
        """Restituisce le chiavi logiche da proteggere per un login."""
        return (
            ("pair", identifier, ip_address),
            ("identifier", identifier, ACCOUNT_SCOPE_IP),
            ("ip", IP_SCOPE_IDENTIFIER, ip_address),
        )

    def _max_attempts_for_scope(self, scope_name: str) -> int:
        """Restituisce la soglia massima per lo scope richiesto."""
        if scope_name == "identifier":
            return settings.login_rate_limit_identifier_max_attempts
        if scope_name == "ip":
            return settings.login_rate_limit_ip_max_attempts
        return settings.login_rate_limit_max_attempts
