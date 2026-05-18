"""Servizio applicativo del modulo Auth."""

from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security.hashing import PasswordHasher
from app.core.security.jwt import JwtTokenManager
from app.core.security.request_context import SecurityRequestContext
from app.domain.security.enums import AuditEventType
from app.domain.security.exceptions import InactiveUserError, InvalidTokenError
from app.models.security.audit_log import AuditLog
from app.models.security.refresh_token import RefreshToken
from app.models.security.user import User
from app.repositories.security.audit_repository import AuditRepository
from app.repositories.security.login_protection_repository import LoginProtectionRepository
from app.repositories.security.refresh_token_repository import RefreshTokenRepository
from app.repositories.security.role_repository import RoleRepository
from app.repositories.security.user_repository import UserRepository
from app.schemas.auth.requests import LoginRequest
from app.schemas.auth.responses import (
    AuthSessionResponse,
    CurrentUserResponse,
    LogoutResponse,
)
from app.services.auth.login_protection_service import LoginProtectionService


@dataclass(slots=True)
class AuthSessionResult:
    """Risultato interno del flusso auth con risposta pubblica e refresh token privato."""

    response: AuthSessionResponse
    refresh_token: str


class AuthService:
    """Servizio applicativo per i flussi di autenticazione."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.user_repository = UserRepository(session)
        self.role_repository = RoleRepository(session)
        self.refresh_token_repository = RefreshTokenRepository(session)
        self.audit_repository = AuditRepository(session)
        self.login_protection_service = LoginProtectionService(LoginProtectionRepository(session))
        self.password_hasher = PasswordHasher()
        self.jwt_token_manager = JwtTokenManager()

    async def login(
        self,
        payload: LoginRequest,
        request_context: SecurityRequestContext,
    ) -> AuthSessionResult:
        """Autentica un utente contro PostgreSQL."""
        identifier = payload.identifier.strip()
        lock_key_ip = request_context.ip_address or "unknown"
        lock_state = await self.login_protection_service.get_lock_result(identifier, lock_key_ip)
        if lock_state.locked_until is not None:
            await self._registra_evento_audit(
                event_type=AuditEventType.LOGIN_COOLDOWN_ACTIVE.value,
                payload_json={
                    "identificativo": identifier,
                    "scope_attivi": lock_state.active_scopes,
                },
                request_context=request_context,
            )
            self.session.commit()
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Troppi tentativi di accesso. Riprovare piu tardi.",
            )

        user = await self.user_repository.get_user_by_username(identifier)
        if user is None or not self.password_hasher.verify_password(
            payload.password,
            user.password_hash,
        ):
            protection_state = await self.login_protection_service.register_failed_attempt(
                identifier=identifier,
                ip_address=lock_key_ip,
            )
            await self._registra_evento_audit(
                event_type=AuditEventType.LOGIN_FAILED.value,
                payload_json={
                    "identificativo": identifier,
                    "tentativi_falliti": protection_state.failed_count,
                    "scope_attivi": protection_state.active_scopes,
                },
                request_context=request_context,
            )
            if protection_state.locked_until is not None:
                await self._registra_evento_audit(
                    event_type=AuditEventType.LOGIN_RATE_LIMITED.value,
                    payload_json={
                        "identificativo": identifier,
                        "bloccato_fino": protection_state.locked_until.isoformat(),
                        "scope_attivi": protection_state.active_scopes,
                    },
                    request_context=request_context,
                )
            self.session.commit()
            if protection_state.locked_until is not None:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Troppi tentativi di accesso. Riprovare piu tardi.",
                )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenziali non valide."
            )

        if not user.is_active:
            await self._registra_evento_audit(
                event_type=AuditEventType.ACCESS_DENIED.value,
                user_id=user.id,
                payload_json={"motivo": "Utente non attivo in fase di login."},
                request_context=request_context,
            )
            self.session.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenziali non valide.",
            )

        await self.login_protection_service.clear_state(identifier, lock_key_ip)
        token_response = await self._genera_token_response(user, request_context)
        user.last_login_at = datetime.now(UTC)
        await self.user_repository.update_user(user)
        await self._registra_evento_audit(
            event_type=AuditEventType.LOGIN_SUCCESS.value,
            user_id=user.id,
            payload_json={"username": user.username},
            request_context=request_context,
        )
        self.session.commit()
        return token_response

    async def refresh(
        self,
        refresh_token_value: str,
        request_context: SecurityRequestContext,
    ) -> AuthSessionResult:
        """Aggiorna le credenziali di accesso usando un refresh token persistito."""
        try:
            decoded = self.jwt_token_manager.decode_token(refresh_token_value)
        except InvalidTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            ) from exc
        if decoded.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token non valido.",
            )

        token_identifier = decoded.get("jti")
        user_id = decoded.get("sub")
        if token_identifier is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token non valido.",
            )

        refresh_token = await self.refresh_token_repository.get_active_by_identifier(
            token_identifier
        )
        if refresh_token is None or refresh_token.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token non valido o revocato.",
            )

        user = await self.user_repository.get_user(user_id)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utente associato al refresh token non valido.",
            )

        await self.refresh_token_repository.revoke(
            token_identifier=token_identifier,
            revoked_reason="Rotazione refresh token.",
        )
        token_response = await self._genera_token_response(user, request_context)
        await self._registra_evento_audit(
            event_type=AuditEventType.TOKEN_REFRESH.value,
            user_id=user.id,
            payload_json={"username": user.username},
            request_context=request_context,
        )
        self.session.commit()
        return token_response

    async def logout(
        self,
        current_user: CurrentUserResponse,
        request_context: SecurityRequestContext,
    ) -> LogoutResponse:
        """Revoca tutte le sessioni refresh attive dell'utente corrente."""
        await self.refresh_token_repository.revoke_all_for_user(
            user_id=current_user.id,
            revoked_reason="Logout utente.",
        )
        await self._registra_evento_audit(
            event_type=AuditEventType.LOGOUT.value,
            user_id=current_user.id,
            payload_json={"username": current_user.username},
            request_context=request_context,
        )
        self.session.commit()
        return LogoutResponse(success=True)

    async def get_current_user(self, token: str) -> CurrentUserResponse:
        """Risolve l'utente corrente a partire da un access token JWT."""
        decoded = self.jwt_token_manager.decode_token(token)
        if decoded.get("type") != "access":
            raise InvalidTokenError("Access token non valido.")

        user_id = decoded.get("sub")
        if user_id is None:
            raise InvalidTokenError("Access token non valido.")

        user = await self.user_repository.get_user(user_id)
        if user is None:
            raise InvalidTokenError("Utente associato al token non trovato.")
        if not user.is_active:
            raise InactiveUserError("Utente non attivo.")
        return await self._crea_risposta_utente(user)

    async def _genera_token_response(
        self,
        user: User,
        request_context: SecurityRequestContext,
    ) -> AuthSessionResult:
        """Genera access token, refresh token e profilo utente corrente."""
        current_user = await self._crea_risposta_utente(user)
        access_token = self.jwt_token_manager.create_access_token(
            subject=user.id,
            claims={"role_code": user.role_code},
        )
        refresh_token, token_identifier, expires_at = self.jwt_token_manager.create_refresh_token(
            subject=user.id,
            claims={"role_code": user.role_code},
        )
        await self.refresh_token_repository.persist(
            RefreshToken(
                user_id=user.id,
                token_identifier=token_identifier,
                issued_at=datetime.now(UTC),
                expires_at=expires_at,
                ip_address=request_context.ip_address,
                user_agent=request_context.user_agent,
            )
        )
        return AuthSessionResult(
            response=AuthSessionResponse(
                access_token=access_token,
                user=current_user,
            ),
            refresh_token=refresh_token,
        )

    async def _crea_risposta_utente(self, user: User) -> CurrentUserResponse:
        """Converte il modello utente in schema di risposta autenticato."""
        permissions = await self.role_repository.list_permissions_by_role(user.role_code)
        return CurrentUserResponse(
            id=user.id,
            username=user.username,
            role_code=user.role_code,
            is_active=user.is_active,
            person_id=user.person_id,
            tenant_id=user.tenant_id,
            permissions=permissions,
        )

    async def _registra_evento_audit(
        self,
        event_type: str,
        request_context: SecurityRequestContext,
        user_id: str | None = None,
        payload_json: dict | None = None,
    ) -> None:
        """Registra un evento di audit sullo schema security."""
        await self.audit_repository.log_event(
            AuditLog(
                user_id=user_id,
                event_type=event_type,
                resource_type="auth",
                resource_id=user_id,
                payload_json=payload_json,
                ip_address=request_context.ip_address,
                user_agent=request_context.user_agent,
            )
        )
