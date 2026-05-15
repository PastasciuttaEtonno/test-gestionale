"""Servizio applicativo del modulo Auth."""

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security.hashing import PasswordHasher
from app.core.security.jwt import JwtTokenManager
from app.domain.security.enums import AuditEventType
from app.domain.security.exceptions import InactiveUserError, InvalidTokenError
from app.models.security.audit_log import AuditLog
from app.models.security.refresh_token import RefreshToken
from app.models.security.user import User
from app.repositories.security.audit_repository import AuditRepository
from app.repositories.security.refresh_token_repository import RefreshTokenRepository
from app.repositories.security.role_repository import RoleRepository
from app.repositories.security.user_repository import UserRepository
from app.schemas.auth.requests import LoginRequest, RefreshTokenRequest
from app.schemas.auth.responses import (
    CurrentUserResponse,
    LogoutResponse,
    TokenPairResponse,
)


class AuthService:
    """Servizio applicativo per i flussi di autenticazione."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.user_repository = UserRepository(session)
        self.role_repository = RoleRepository(session)
        self.refresh_token_repository = RefreshTokenRepository(session)
        self.audit_repository = AuditRepository(session)
        self.password_hasher = PasswordHasher()
        self.jwt_token_manager = JwtTokenManager()

    async def login(self, payload: LoginRequest) -> TokenPairResponse:
        """Autentica un utente contro PostgreSQL."""
        user = await self.user_repository.get_user_by_username(payload.identifier)
        if user is None or not self.password_hasher.verify_password(
            payload.password,
            user.password_hash,
        ):
            await self._registra_evento_audit(
                event_type=AuditEventType.LOGIN_FAILED.value,
                payload_json={"identificativo": payload.identifier},
            )
            self.session.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenziali non valide.",
            )

        if not user.is_active:
            await self._registra_evento_audit(
                event_type=AuditEventType.ACCESS_DENIED.value,
                user_id=user.id,
                payload_json={"motivo": "Utente non attivo in fase di login."},
            )
            self.session.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Utente non attivo.",
            )

        token_response = await self._genera_token_response(user)
        user.last_login_at = datetime.now(UTC)
        await self.user_repository.update_user(user)
        await self._registra_evento_audit(
            event_type=AuditEventType.LOGIN_SUCCESS.value,
            user_id=user.id,
            payload_json={"username": user.username},
        )
        self.session.commit()
        return token_response

    async def refresh(self, payload: RefreshTokenRequest) -> TokenPairResponse:
        """Aggiorna le credenziali di accesso usando un refresh token persistito."""
        try:
            decoded = self.jwt_token_manager.decode_token(payload.refresh_token)
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
        token_response = await self._genera_token_response(user)
        await self._registra_evento_audit(
            event_type=AuditEventType.TOKEN_REFRESH.value,
            user_id=user.id,
            payload_json={"username": user.username},
        )
        self.session.commit()
        return token_response

    async def logout(self, current_user: CurrentUserResponse) -> LogoutResponse:
        """Revoca tutte le sessioni refresh attive dell'utente corrente."""
        await self.refresh_token_repository.revoke_all_for_user(
            user_id=current_user.id,
            revoked_reason="Logout utente.",
        )
        await self._registra_evento_audit(
            event_type=AuditEventType.LOGOUT.value,
            user_id=current_user.id,
            payload_json={"username": current_user.username},
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

    async def _genera_token_response(self, user: User) -> TokenPairResponse:
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
                ip_address=None,
                user_agent=None,
            )
        )
        return TokenPairResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=current_user,
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
                ip_address=None,
                user_agent=None,
            )
        )
