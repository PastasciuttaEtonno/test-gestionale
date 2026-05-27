"""Dependency RBAC dichiarative e tenant-aware.

Pattern di autorizzazione nel progetto
---------------------------------------
Esistono due pattern distinti e non intercambiabili:

1. RequirePermission (questo modulo) — risorse di dominio
   Usare per: Anagrafiche, BOM, Finance e qualsiasi futuro modulo business.
   - Controlla il permission_code contro current_user.permissions (RBAC granulare).
   - Verifica opzionalmente che la risorsa target appartenga al tenant dell'utente.
   - Il service riceve current_user.tenant_id e filtra sempre entro quel perimetro.
   - Presuppone che ogni utente abbia un tenant_id valorizzato.

2. Role guard + scoping nel service (deps/auth.py) — risorse identity/security
   Usare per: Users, Tenants, Audit e risorse amministrative cross-tenant.
   - Controlla il role_code (require_admin, require_tenant_admin, require_admin_or_tenant_admin).
   - L'admin ha tenant_id=None e necessita di visibilità cross-tenant: la logica
     di filtraggio deve stare nel service (es. _get_scoped_user, _list_users_for_actor)
     perché cambia la semantica della query, non solo il filtro WHERE.
   - RequirePermission non può coprire questo caso senza eccezioni speciali per l'admin.

Regola decisionale per nuovi moduli
-------------------------------------
  Risorsa sempre appartenente a un tenant?  →  RequirePermission
  Risorsa con visibilità cross-tenant per admin?  →  role guard + service scoping
"""

from collections.abc import Awaitable, Callable
from json import JSONDecodeError

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps.auth import get_active_user
from app.core.db import get_db_session
from app.schemas.auth.responses import CurrentUserResponse

type TenantResolver = Callable[[Session, str], Awaitable[str | None]]


class RequirePermission:
    """Dependency RBAC dichiarativa con supporto tenant-aware."""

    def __init__(
        self,
        resource: str,
        action: str,
        *,
        tenant_field_name: str | None = None,
        resource_id_param_name: str | None = None,
        tenant_resolver: TenantResolver | None = None,
    ) -> None:
        self.permission_code = f"{resource}.{action}"
        self.tenant_field_name = tenant_field_name
        self.resource_id_param_name = resource_id_param_name
        self.tenant_resolver = tenant_resolver

    async def __call__(
        self,
        request: Request,
        current_user: CurrentUserResponse = Depends(get_active_user),
        session: Session = Depends(get_db_session),
    ) -> CurrentUserResponse:
        """Verifica permesso e appartenenza tenant della risorsa target."""
        if self.permission_code not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permesso negato.",
            )

        target_tenant_id = await self._resolve_target_tenant_id(request, session)
        if target_tenant_id is None:
            return current_user

        if current_user.tenant_id is not None and target_tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Risorsa non accessibile per il tenant corrente.",
            )

        return current_user

    async def _resolve_target_tenant_id(
        self,
        request: Request,
        session: Session,
    ) -> str | None:
        """Ricava il tenant target dal body, dai path params o dal database."""
        if self.tenant_resolver is not None:
            if self.resource_id_param_name is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Configurazione RBAC non valida.",
                )
            resource_id = request.path_params.get(self.resource_id_param_name)
            if not resource_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Identificativo risorsa mancante.",
                )
            tenant_id = await self.tenant_resolver(session, str(resource_id))
            if tenant_id is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Risorsa non trovata.",
                )
            return tenant_id

        if self.tenant_field_name is None:
            return None

        tenant_id = request.path_params.get(self.tenant_field_name)
        if tenant_id:
            return str(tenant_id)

        tenant_id = request.query_params.get(self.tenant_field_name)
        if tenant_id:
            return str(tenant_id)

        body = {}
        if request.method in {"POST", "PUT", "PATCH"}:
            try:
                body = await request.json()
            except JSONDecodeError:
                body = {}
        if isinstance(body, dict):
            tenant_id = body.get(self.tenant_field_name)
            if tenant_id:
                return str(tenant_id)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant target non presente nella richiesta.",
        )
