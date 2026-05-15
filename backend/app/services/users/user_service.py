"""Servizio utenti persistito su PostgreSQL."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security.hashing import PasswordHasher
from app.domain.security.constants import ADMIN_ROLE, TENANT_ADMIN_ROLE
from app.domain.security.enums import AuditEventType
from app.models.security.audit_log import AuditLog
from app.models.security.user import User
from app.repositories.security.audit_repository import AuditRepository
from app.repositories.security.role_repository import RoleRepository
from app.repositories.security.tenant_repository import TenantRepository
from app.repositories.security.user_repository import UserRepository
from app.schemas.auth.responses import CurrentUserResponse
from app.schemas.users.requests import (
    ChangeUserRoleRequest,
    ChangeUserStatusRequest,
    CreateUserRequest,
    UpdateUserRequest,
)
from app.schemas.users.responses import UserListResponse, UserResponse


class UserNotFoundError(Exception):
    """Sollevata quando un utente non puo essere trovato."""


class UserService:
    """Servizio applicativo per la gestione utenti."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.user_repository = UserRepository(session)
        self.role_repository = RoleRepository(session)
        self.tenant_repository = TenantRepository(session)
        self.audit_repository = AuditRepository(session)
        self.password_hasher = PasswordHasher()

    async def list_users(self, actor_user: CurrentUserResponse) -> UserListResponse:
        """Restituisce l'elenco utenti visibile all'attore corrente."""
        users = await self._list_users_for_actor(actor_user)
        items = [self._to_response(user) for user in users]
        return UserListResponse(items=items, total=len(items))

    async def get_user(self, user_id: str, actor_user: CurrentUserResponse) -> UserResponse:
        """Restituisce un singolo utente nel perimetro dell'attore corrente."""
        user = await self._get_scoped_user(user_id=user_id, actor_user=actor_user)
        if user is None:
            raise UserNotFoundError(f"Utente '{user_id}' non trovato.")
        return self._to_response(user)

    async def create_user(
        self,
        payload: CreateUserRequest,
        actor_user: CurrentUserResponse,
    ) -> UserResponse:
        """Crea un utente persistendolo su PostgreSQL."""
        existing = await self.user_repository.get_user_by_username(payload.username)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esiste gia un utente con questo username.",
            )
        if payload.email:
            existing_email = await self.user_repository.get_user_by_email(payload.email)
            if existing_email is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Esiste gia un utente con questa email.",
                )

        role = await self.role_repository.get_role(payload.role_code)
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ruolo richiesto non trovato.",
            )

        tenant_id = await self._resolve_target_tenant_id(payload=payload, actor_user=actor_user)

        user = await self.user_repository.create_user(
            User(
                username=payload.username,
                email=payload.email,
                password_hash=self.password_hasher.hash_password(payload.password),
                role_code=payload.role_code,
                is_active=payload.is_active,
                person_id=payload.person_id,
                tenant_id=tenant_id,
            )
        )
        await self._registra_evento_audit(
            event_type=AuditEventType.USER_CREATED.value,
            actor_user_id=actor_user.id,
            target_user_id=user.id,
            payload_json={
                "attore": actor_user.username,
                "username_creato": user.username,
                "ruolo": user.role_code,
                "stato_attivo": user.is_active,
                "tenant_id": user.tenant_id,
            },
        )
        self.session.commit()
        return self._to_response(user)

    async def update_user(
        self,
        user_id: str,
        payload: UpdateUserRequest,
        actor_user: CurrentUserResponse,
    ) -> UserResponse:
        """Aggiorna un utente."""
        user = await self._get_scoped_user(user_id=user_id, actor_user=actor_user)
        if user is None:
            raise UserNotFoundError(f"Utente '{user_id}' non trovato.")

        email_precedente = user.email
        person_id_precedente = user.person_id

        if payload.email and payload.email != user.email:
            existing_email = await self.user_repository.get_user_by_email(payload.email)
            if existing_email is not None and existing_email.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Esiste gia un utente con questa email.",
                )

        user.email = payload.email if payload.email is not None else user.email
        user.person_id = payload.person_id if payload.person_id is not None else user.person_id
        updated = await self.user_repository.update_user(user)
        await self._registra_evento_audit(
            event_type=AuditEventType.USER_UPDATED.value,
            actor_user_id=actor_user.id,
            target_user_id=updated.id,
            payload_json={
                "attore": actor_user.username,
                "username_target": updated.username,
                "email_precedente": email_precedente,
                "email_nuova": updated.email,
                "person_id_precedente": person_id_precedente,
                "person_id_nuovo": updated.person_id,
            },
        )
        self.session.commit()
        return self._to_response(updated)

    async def change_status(
        self,
        user_id: str,
        payload: ChangeUserStatusRequest,
        actor_user: CurrentUserResponse,
    ) -> UserResponse:
        """Modifica lo stato attivo di un utente."""
        user = await self._get_scoped_user(user_id=user_id, actor_user=actor_user)
        if user is None:
            raise UserNotFoundError(f"Utente '{user_id}' non trovato.")

        stato_precedente = user.is_active
        user.is_active = payload.is_active
        updated = await self.user_repository.update_user(user)
        await self._registra_evento_audit(
            event_type=AuditEventType.USER_STATUS_CHANGED.value,
            actor_user_id=actor_user.id,
            target_user_id=updated.id,
            payload_json={
                "attore": actor_user.username,
                "username_target": updated.username,
                "stato_precedente": stato_precedente,
                "stato_nuovo": updated.is_active,
            },
        )
        self.session.commit()
        return self._to_response(updated)

    async def change_role(
        self,
        user_id: str,
        payload: ChangeUserRoleRequest,
        actor_user: CurrentUserResponse,
    ) -> UserResponse:
        """Modifica il ruolo di un utente."""
        user = await self._get_scoped_user(user_id=user_id, actor_user=actor_user)
        if user is None:
            raise UserNotFoundError(f"Utente '{user_id}' non trovato.")

        self._validate_role_assignment(payload.role_code, actor_user)
        role = await self.role_repository.get_role(payload.role_code)
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ruolo richiesto non trovato.",
            )

        ruolo_precedente = user.role_code
        user.role_code = payload.role_code
        updated = await self.user_repository.update_user(user)
        await self._registra_evento_audit(
            event_type=AuditEventType.USER_ROLE_CHANGED.value,
            actor_user_id=actor_user.id,
            target_user_id=updated.id,
            payload_json={
                "attore": actor_user.username,
                "username_target": updated.username,
                "ruolo_precedente": ruolo_precedente,
                "ruolo_nuovo": updated.role_code,
            },
        )
        self.session.commit()
        return self._to_response(updated)

    def _to_response(self, user: User) -> UserResponse:
        """Converte il modello ORM utente nello schema di risposta."""
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role_code=user.role_code,
            is_active=user.is_active,
            person_id=user.person_id,
            tenant_id=user.tenant_id,
        )

    async def _list_users_for_actor(self, actor_user: CurrentUserResponse) -> list[User]:
        """Restituisce la lista utenti compatibile con il perimetro dell'attore."""
        if actor_user.role_code == TENANT_ADMIN_ROLE:
            tenant_id = self._require_actor_tenant(actor_user)
            return await self.user_repository.list_users_by_tenant(tenant_id)
        return await self.user_repository.list_users()

    async def _get_scoped_user(
        self,
        user_id: str,
        actor_user: CurrentUserResponse,
    ) -> User | None:
        """Restituisce un utente applicando il perimetro del ruolo chiamante."""
        if actor_user.role_code == TENANT_ADMIN_ROLE:
            tenant_id = self._require_actor_tenant(actor_user)
            return await self.user_repository.get_user_by_tenant(
                user_id=user_id, tenant_id=tenant_id
            )
        return await self.user_repository.get_user(user_id)

    async def _resolve_target_tenant_id(
        self,
        payload: CreateUserRequest,
        actor_user: CurrentUserResponse,
    ) -> str | None:
        """Determina e valida il tenant target del nuovo utente."""
        self._validate_role_assignment(payload.role_code, actor_user)

        if actor_user.role_code == TENANT_ADMIN_ROLE:
            tenant_id = self._require_actor_tenant(actor_user)
            if payload.tenant_id is not None and payload.tenant_id != tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Il tenant admin non puo creare utenti fuori dal proprio tenant.",
                )
            return tenant_id

        if payload.role_code == ADMIN_ROLE:
            if payload.tenant_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Un super admin non puo essere associato a un tenant.",
                )
            return None

        if payload.tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Il tenant e obbligatorio per utenti tenant-scoped.",
            )

        tenant = await self.tenant_repository.get_tenant(payload.tenant_id)
        if tenant is None or not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant richiesto non trovato o non attivo.",
            )
        return tenant.id

    def _validate_role_assignment(
        self,
        target_role_code: str,
        actor_user: CurrentUserResponse,
    ) -> None:
        """Valida se l'attore puo assegnare il ruolo richiesto."""
        if actor_user.role_code == TENANT_ADMIN_ROLE and target_role_code == ADMIN_ROLE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Il tenant admin non puo assegnare il ruolo admin.",
            )

    def _require_actor_tenant(self, actor_user: CurrentUserResponse) -> str:
        """Restituisce il tenant dell'attore o interrompe se mancante."""
        if actor_user.tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="L'utente corrente non e associato ad alcun tenant.",
            )
        return actor_user.tenant_id

    async def _registra_evento_audit(
        self,
        event_type: str,
        actor_user_id: str,
        target_user_id: str,
        payload_json: dict,
    ) -> None:
        """Registra un evento di audit per operazioni amministrative utenti."""
        await self.audit_repository.log_event(
            AuditLog(
                user_id=actor_user_id,
                event_type=event_type,
                resource_type="user",
                resource_id=target_user_id,
                payload_json=payload_json,
                ip_address=None,
                user_agent=None,
            )
        )
