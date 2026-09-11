"""Servizio applicativo per il modulo Anagrafiche."""

from fastapi import HTTPException, status

from app.models.core.anagrafica import Anagrafica
from app.models.core.anagrafica_indirizzo import AnagraficaIndirizzo
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


class AnagraficaNotFoundError(Exception):
    """Sollevata quando un'anagrafica non viene trovata nel tenant corrente."""


class AnagraficaService:
    """Casi d'uso del modulo Anagrafiche."""

    def __init__(self, repository: AnagraficaRepository) -> None:
        self.repository = repository

    def list_anagrafiche(
        self, tenant_id: str, params: AnagraficaListParams
    ) -> AnagraficaListResponse:
        """Restituisce la lista paginata delle anagrafiche del tenant."""
        items, total = self.repository.list(
            tenant_id,
            tipo=params.tipo,
            is_active=params.is_active,
            q=params.q,
            skip=params.skip,
            limit=params.limit,
        )
        return AnagraficaListResponse(
            items=[AnagraficaResponse.model_validate(a) for a in items],
            total=total,
            skip=params.skip,
            limit=params.limit,
        )

    def get_anagrafica(self, tenant_id: str, anagrafica_id: str) -> AnagraficaResponse:
        """Restituisce una singola anagrafica del tenant."""
        record = self.repository.get(tenant_id, anagrafica_id)
        if record is None:
            raise AnagraficaNotFoundError(anagrafica_id)
        return AnagraficaResponse.model_validate(record)

    def create_anagrafica(
        self, tenant_id: str, payload: AnagraficaCreateRequest
    ) -> AnagraficaResponse:
        """Crea una nuova anagrafica con eventuali indirizzi."""
        anagrafica = Anagrafica(
            tenant_id=tenant_id,
            tipo=payload.tipo,
            is_persona_fisica=payload.is_persona_fisica,
            ragione_sociale=payload.ragione_sociale,
            cognome=payload.cognome,
            nome=payload.nome,
            partita_iva=payload.partita_iva,
            codice_fiscale=payload.codice_fiscale,
            codice_sdi=payload.codice_sdi or ("0000000" if payload.pec else None),
            pec=payload.pec,
            regime_fiscale=payload.regime_fiscale,
            natura_giuridica=payload.natura_giuridica,
            email=payload.email,
            telefono=payload.telefono,
            website=payload.website,
            note=payload.note,
        )
        for addr in payload.indirizzi:
            anagrafica.indirizzi.append(
                AnagraficaIndirizzo(
                    tipo=addr.tipo,
                    is_principale=addr.is_principale,
                    indirizzo=addr.indirizzo,
                    citta=addr.citta,
                    cap=addr.cap,
                    provincia=addr.provincia,
                    paese=addr.paese,
                )
            )
        saved = self.repository.create(anagrafica)
        return AnagraficaResponse.model_validate(saved)

    def update_anagrafica(
        self, tenant_id: str, anagrafica_id: str, payload: AnagraficaUpdateRequest
    ) -> AnagraficaResponse:
        """Aggiorna parzialmente un'anagrafica."""
        record = self._get_or_404(tenant_id, anagrafica_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(record, field, value)
        saved = self.repository.update(record)
        return AnagraficaResponse.model_validate(saved)

    def delete_anagrafica(self, tenant_id: str, anagrafica_id: str) -> None:
        """Soft delete: imposta is_active = False."""
        record = self._get_or_404(tenant_id, anagrafica_id)
        record.is_active = False
        self.repository.update(record)

    # ── Indirizzi ──────────────────────────────────────────────────────────

    def add_indirizzo(
        self, tenant_id: str, anagrafica_id: str, payload: IndirizzoCreateRequest
    ) -> IndirizzoResponse:
        """Aggiunge un indirizzo a un'anagrafica del tenant."""
        self._get_or_404(tenant_id, anagrafica_id)
        indirizzo = AnagraficaIndirizzo(
            anagrafica_id=anagrafica_id,
            tipo=payload.tipo,
            is_principale=payload.is_principale,
            indirizzo=payload.indirizzo,
            citta=payload.citta,
            cap=payload.cap,
            provincia=payload.provincia,
            paese=payload.paese,
        )
        saved = self.repository.create_indirizzo(indirizzo)
        return IndirizzoResponse.model_validate(saved)

    def update_indirizzo(
        self,
        tenant_id: str,
        anagrafica_id: str,
        indirizzo_id: str,
        payload: IndirizzoUpdateRequest,
    ) -> IndirizzoResponse:
        """Aggiorna parzialmente un indirizzo."""
        self._get_or_404(tenant_id, anagrafica_id)
        record = self.repository.get_indirizzo(anagrafica_id, indirizzo_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Indirizzo non trovato."
            )
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(record, field, value)
        saved = self.repository.update_indirizzo(record)
        return IndirizzoResponse.model_validate(saved)

    def delete_indirizzo(self, tenant_id: str, anagrafica_id: str, indirizzo_id: str) -> None:
        """Rimuove un indirizzo."""
        self._get_or_404(tenant_id, anagrafica_id)
        record = self.repository.get_indirizzo(anagrafica_id, indirizzo_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Indirizzo non trovato."
            )
        self.repository.delete_indirizzo(record)

    # ── Helpers ────────────────────────────────────────────────────────────

    def _get_or_404(self, tenant_id: str, anagrafica_id: str) -> Anagrafica:
        record = self.repository.get(tenant_id, anagrafica_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Anagrafica non trovata.",
            )
        return record
