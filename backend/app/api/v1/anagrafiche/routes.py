"""Route del modulo Anagrafiche."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps.rbac import RequirePermission
from app.core.db import get_db_session
from app.repositories.core.anagrafica_repository import AnagraficaRepository
from app.schemas.anagrafiche.requests import (
    AnagraficaCreateRequest,
    AnagraficaListParams,
    AnagraficaUpdateRequest,
    IndirizzoCreateRequest,
    IndirizzoUpdateRequest,
)
from app.schemas.anagrafiche.responses import (
    AnagraficaListResponse,
    AnagraficaResponse,
    IndirizzoResponse,
)
from app.schemas.auth.responses import CurrentUserResponse
from app.services.anagrafiche.anagrafica_service import AnagraficaService

router = APIRouter(tags=["Anagrafiche"])

_read = RequirePermission("anagrafiche", "read")
_write = RequirePermission("anagrafiche", "write")
_delete = RequirePermission("anagrafiche", "delete")


def _service(session: Session = Depends(get_db_session)) -> AnagraficaService:
    return AnagraficaService(AnagraficaRepository(session))


@router.get(
    "",
    response_model=AnagraficaListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Lista anagrafiche restituita con successo."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso anagrafiche.read richiesto."},
    },
    summary="Elenca le anagrafiche del tenant",
)
def list_anagrafiche(
    tipo: str | None = Query(default=None, description="Filtra per tipo soggetto."),
    is_active: bool = Query(default=True, description="Filtra per stato attivo."),
    q: str | None = Query(default=None, description="Ricerca testuale."),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: CurrentUserResponse = Depends(_read),
    service: AnagraficaService = Depends(_service),
) -> AnagraficaListResponse:
    """Restituisce la lista paginata delle anagrafiche del tenant corrente.

    Supporta filtro per tipo, stato attivo e ricerca testuale su ragione
    sociale, cognome, partita IVA e codice fiscale.
    """
    params = AnagraficaListParams(tipo=tipo, is_active=is_active, q=q, skip=skip, limit=limit)
    return service.list_anagrafiche(current_user.tenant_id, params)


@router.post(
    "",
    response_model=AnagraficaResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Anagrafica creata con successo."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso anagrafiche.write richiesto."},
        422: {"description": "Dati non validi (es. ragione_sociale mancante per ente)."},
    },
    summary="Crea una nuova anagrafica",
)
def create_anagrafica(
    payload: AnagraficaCreateRequest,
    current_user: CurrentUserResponse = Depends(_write),
    service: AnagraficaService = Depends(_service),
) -> AnagraficaResponse:
    """Crea un nuovo soggetto (cliente, fornitore, agente, ecc.) nel tenant corrente.

    Se vengono forniti indirizzi nel payload, vengono creati contestualmente.
    """
    return service.create_anagrafica(current_user.tenant_id, payload)


@router.get(
    "/{anagrafica_id}",
    response_model=AnagraficaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Anagrafica restituita con successo."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso anagrafiche.read richiesto."},
        404: {"description": "Anagrafica non trovata."},
    },
    summary="Dettaglio anagrafica",
)
def get_anagrafica(
    anagrafica_id: str,
    current_user: CurrentUserResponse = Depends(_read),
    service: AnagraficaService = Depends(_service),
) -> AnagraficaResponse:
    """Restituisce il dettaglio completo di un'anagrafica del tenant, inclusi gli indirizzi."""
    return service.get_anagrafica(current_user.tenant_id, anagrafica_id)


@router.patch(
    "/{anagrafica_id}",
    response_model=AnagraficaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Anagrafica aggiornata con successo."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso anagrafiche.write richiesto."},
        404: {"description": "Anagrafica non trovata."},
    },
    summary="Aggiorna un'anagrafica",
)
def update_anagrafica(
    anagrafica_id: str,
    payload: AnagraficaUpdateRequest,
    current_user: CurrentUserResponse = Depends(_write),
    service: AnagraficaService = Depends(_service),
) -> AnagraficaResponse:
    """Aggiorna parzialmente un'anagrafica del tenant. Solo i campi presenti nel payload vengono modificati."""
    return service.update_anagrafica(current_user.tenant_id, anagrafica_id, payload)


@router.delete(
    "/{anagrafica_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Anagrafica disattivata con successo."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso anagrafiche.delete richiesto."},
        404: {"description": "Anagrafica non trovata."},
    },
    summary="Disattiva un'anagrafica (soft delete)",
)
def delete_anagrafica(
    anagrafica_id: str,
    current_user: CurrentUserResponse = Depends(_delete),
    service: AnagraficaService = Depends(_service),
) -> None:
    """Esegue il soft-delete impostando is_active = false. L'anagrafica non viene cancellata fisicamente."""
    service.delete_anagrafica(current_user.tenant_id, anagrafica_id)


# ── Indirizzi ──────────────────────────────────────────────────────────────


@router.post(
    "/{anagrafica_id}/indirizzi",
    response_model=IndirizzoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Aggiunge un indirizzo a un'anagrafica",
)
def add_indirizzo(
    anagrafica_id: str,
    payload: IndirizzoCreateRequest,
    current_user: CurrentUserResponse = Depends(_write),
    service: AnagraficaService = Depends(_service),
) -> IndirizzoResponse:
    """Aggiunge un nuovo indirizzo all'anagrafica specificata."""
    return service.add_indirizzo(current_user.tenant_id, anagrafica_id, payload)


@router.patch(
    "/{anagrafica_id}/indirizzi/{indirizzo_id}",
    response_model=IndirizzoResponse,
    status_code=status.HTTP_200_OK,
    summary="Aggiorna un indirizzo",
)
def update_indirizzo(
    anagrafica_id: str,
    indirizzo_id: str,
    payload: IndirizzoUpdateRequest,
    current_user: CurrentUserResponse = Depends(_write),
    service: AnagraficaService = Depends(_service),
) -> IndirizzoResponse:
    """Aggiorna parzialmente un indirizzo dell'anagrafica."""
    return service.update_indirizzo(current_user.tenant_id, anagrafica_id, indirizzo_id, payload)


@router.delete(
    "/{anagrafica_id}/indirizzi/{indirizzo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Rimuove un indirizzo",
)
def delete_indirizzo(
    anagrafica_id: str,
    indirizzo_id: str,
    current_user: CurrentUserResponse = Depends(_write),
    service: AnagraficaService = Depends(_service),
) -> None:
    """Rimuove fisicamente un indirizzo dall'anagrafica."""
    service.delete_indirizzo(current_user.tenant_id, anagrafica_id, indirizzo_id)
