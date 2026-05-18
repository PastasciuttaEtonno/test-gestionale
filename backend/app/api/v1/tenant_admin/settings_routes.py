"""Route di configurazione tenant admin."""

from fastapi import APIRouter, Depends, HTTPException, Path, status
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.api.deps.auth import require_tenant_admin
from app.core.db import get_db_session
from app.core.redis import get_redis_client
from app.schemas.auth.responses import CurrentUserResponse
from app.schemas.tenant_admin.requests import (
    UpdateCompanySettingsRequest,
    UpdateDocumentSequenceRequest,
    UpdateSmtpSettingsRequest,
)
from app.schemas.tenant_admin.responses import (
    CompanySettingsResponse,
    DocumentSequenceListResponse,
    DocumentSequenceResponse,
    SmtpSettingsResponse,
)
from app.services.tenant_admin.tenant_settings_service import TenantSettingsService

router = APIRouter(tags=["Tenant Admin"])


def get_tenant_settings_service(
    session: Session = Depends(get_db_session),
) -> TenantSettingsService:
    """Restituisce la dependency del servizio impostazioni tenant admin."""
    return TenantSettingsService(session)


@router.get(
    "/company-settings",
    response_model=CompanySettingsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Impostazioni aziendali del tenant restituite con successo."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Ruolo tenant admin richiesto o tenant non associato."},
        404: {"description": "Impostazioni aziendali del tenant non trovate."},
    },
    summary="Recupera le impostazioni aziendali del tenant corrente",
)
async def get_company_settings(
    current_user: CurrentUserResponse = Depends(require_tenant_admin),
    tenant_settings_service: TenantSettingsService = Depends(get_tenant_settings_service),
) -> CompanySettingsResponse:
    """Restituisce i dati aziendali globali della propria organizzazione.

    L'endpoint e limitato al tenant corrente e non espone dati di altre aziende.
    """
    return await tenant_settings_service.get_company_settings(current_user=current_user)


@router.put(
    "/company-settings",
    response_model=CompanySettingsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Impostazioni aziendali del tenant aggiornate con successo."},
        400: {"description": "Payload della richiesta non valido."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Ruolo tenant admin richiesto o tenant non associato."},
        404: {"description": "Tenant corrente non trovato o non attivo."},
    },
    summary="Aggiorna le impostazioni aziendali del tenant corrente",
)
async def update_company_settings(
    payload: UpdateCompanySettingsRequest,
    current_user: CurrentUserResponse = Depends(require_tenant_admin),
    redis_client: Redis = Depends(get_redis_client),
    tenant_settings_service: TenantSettingsService = Depends(get_tenant_settings_service),
) -> CompanySettingsResponse:
    """Aggiorna anagrafica aziendale, recapiti e branding documentale del tenant."""
    return await tenant_settings_service.update_company_settings(
        payload=payload,
        current_user=current_user,
        redis_client=redis_client,
    )


@router.get(
    "/smtp-settings",
    response_model=SmtpSettingsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Configurazione SMTP del tenant restituita con successo."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Ruolo tenant admin richiesto o tenant non associato."},
        404: {"description": "Configurazione SMTP del tenant non trovata."},
    },
    summary="Recupera la configurazione SMTP del tenant corrente",
)
async def get_smtp_settings(
    current_user: CurrentUserResponse = Depends(require_tenant_admin),
    tenant_settings_service: TenantSettingsService = Depends(get_tenant_settings_service),
) -> SmtpSettingsResponse:
    """Restituisce la configurazione SMTP della propria azienda senza esporre la password."""
    return await tenant_settings_service.get_smtp_settings(current_user=current_user)


@router.put(
    "/smtp-settings",
    response_model=SmtpSettingsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Configurazione SMTP del tenant aggiornata con successo."},
        400: {"description": "Payload della richiesta non valido."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Ruolo tenant admin richiesto o tenant non associato."},
        404: {"description": "Tenant corrente non trovato o non attivo."},
    },
    summary="Aggiorna la configurazione SMTP del tenant corrente",
)
async def update_smtp_settings(
    payload: UpdateSmtpSettingsRequest,
    current_user: CurrentUserResponse = Depends(require_tenant_admin),
    redis_client: Redis = Depends(get_redis_client),
    tenant_settings_service: TenantSettingsService = Depends(get_tenant_settings_service),
) -> SmtpSettingsResponse:
    """Aggiorna la configurazione SMTP del tenant cifrando la password lato backend."""
    return await tenant_settings_service.update_smtp_settings(
        payload=payload,
        current_user=current_user,
        redis_client=redis_client,
    )


@router.get(
    "/document-sequences",
    response_model=DocumentSequenceListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Numerazioni documentali del tenant restituite con successo."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Ruolo tenant admin richiesto o tenant non associato."},
        404: {"description": "Tenant corrente non trovato o non attivo."},
    },
    summary="Elenca le numerazioni documentali del tenant corrente",
)
async def list_document_sequences(
    current_user: CurrentUserResponse = Depends(require_tenant_admin),
    tenant_settings_service: TenantSettingsService = Depends(get_tenant_settings_service),
) -> DocumentSequenceListResponse:
    """Restituisce le numerazioni configurate per la propria organizzazione."""
    return await tenant_settings_service.list_document_sequences(current_user=current_user)


@router.put(
    "/document-sequences/{sequence_code}",
    response_model=DocumentSequenceResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Numerazione documentale aggiornata con successo."},
        400: {"description": "Payload della richiesta non valido."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Ruolo tenant admin richiesto o tenant non associato."},
        404: {"description": "Numerazione documentale o tenant non trovati."},
    },
    summary="Aggiorna una numerazione documentale del tenant corrente",
)
async def update_document_sequence(
    payload: UpdateDocumentSequenceRequest,
    sequence_code: str = Path(
        min_length=1,
        max_length=100,
        description="Codice logico della numerazione documentale da aggiornare.",
        examples=["invoice_electronic"],
    ),
    current_user: CurrentUserResponse = Depends(require_tenant_admin),
    redis_client: Redis = Depends(get_redis_client),
    tenant_settings_service: TenantSettingsService = Depends(get_tenant_settings_service),
) -> DocumentSequenceResponse:
    """Aggiorna una singola numerazione documentale nel perimetro del tenant corrente."""
    try:
        return await tenant_settings_service.update_document_sequence(
            sequence_code=sequence_code,
            payload=payload,
            current_user=current_user,
            redis_client=redis_client,
        )
    except HTTPException:
        raise
