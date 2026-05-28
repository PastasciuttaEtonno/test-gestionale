"""Servizio applicativo per il modulo Bolle / DDT."""

from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import uuid4

from fastapi import HTTPException, status
from redis.asyncio import Redis

from app.core.cache import (
    build_tenant_dashboard_kpis_cache_key,
    invalidate_cache_key_best_effort,
)
from app.models.core.bolla import Bolla
from app.models.core.bolla_riga import BollaRiga
from app.repositories.core.anagrafica_repository import AnagraficaRepository
from app.repositories.core.articolo_repository import ArticoloRepository
from app.repositories.core.bolla_repository import BollaRepository
from app.schemas.bolle.requests import (
    BollaCreateRequest,
    BollaListParams,
    BollaUpdateRequest,
    RigaCreateRequest,
    RigaUpdateRequest,
)
from app.schemas.bolle.responses import BollaListResponse, BollaResponse
from app.schemas.events.sse import EventTypes
from app.services.events.event_publisher import EventPublisher

SEQUENCE_DDT = "delivery_note_italy"
STATO_BOZZA = "bozza"
STATO_EMESSA = "emessa"
STATO_ANNULLATA = "annullata"
_CENT = Decimal("0.01")


class BollaService:
    """Casi d'uso del modulo Bolle: lifecycle, numerazione, totali, eventi."""

    def __init__(
        self,
        repository: BollaRepository,
        anagrafica_repository: AnagraficaRepository,
        articolo_repository: ArticoloRepository,
        redis_client: Redis | None = None,
        event_publisher: EventPublisher | None = None,
    ) -> None:
        self.repository = repository
        self.anagrafica_repository = anagrafica_repository
        self.articolo_repository = articolo_repository
        self.redis_client = redis_client
        self.event_publisher = event_publisher

    # ── Lettura ───────────────────────────────────────────────────────────

    def list_bolle(self, tenant_id: str, params: BollaListParams) -> BollaListResponse:
        """Restituisce la lista paginata delle bolle del tenant."""
        items, total = self.repository.list(
            tenant_id,
            stato=params.stato,
            anagrafica_id=params.anagrafica_id,
            q=params.q,
            skip=params.skip,
            limit=params.limit,
        )
        return BollaListResponse(
            items=[BollaResponse.model_validate(b) for b in items],
            total=total,
            skip=params.skip,
            limit=params.limit,
        )

    def get_bolla(self, tenant_id: str, bolla_id: str) -> BollaResponse:
        """Restituisce una singola bolla del tenant con le righe."""
        return BollaResponse.model_validate(self._get_or_404(tenant_id, bolla_id))

    # ── Creazione / modifica testata (solo bozza) ─────────────────────────

    async def create_bolla(self, tenant_id: str, payload: BollaCreateRequest) -> BollaResponse:
        """Crea una bozza di bolla per il destinatario indicato."""
        self._valida_anagrafica(tenant_id, payload.anagrafica_id)
        bolla = Bolla(
            tenant_id=tenant_id,
            stato=STATO_BOZZA,
            data_documento=payload.data_documento,
            anagrafica_id=payload.anagrafica_id,
            causale_trasporto=payload.causale_trasporto,
            aspetto_beni=payload.aspetto_beni,
            num_colli=payload.num_colli,
            peso_kg=payload.peso_kg,
            trasporto_a_cura=payload.trasporto_a_cura,
            vettore=payload.vettore,
            note=payload.note,
        )
        saved = self.repository.create(bolla)
        self.repository.session.commit()
        await self._notifica(tenant_id, EventTypes.BOLLA_CREATED, {"bolla_id": saved.id})
        return BollaResponse.model_validate(saved)

    async def update_bolla(
        self, tenant_id: str, bolla_id: str, payload: BollaUpdateRequest
    ) -> BollaResponse:
        """Aggiorna la testata di una bozza (optimistic locking via version)."""
        bolla = self._get_or_404(tenant_id, bolla_id)
        self._assert_bozza(bolla)
        if bolla.version != payload.version:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bolla modificata da un altro utente, ricarica la pagina.",
            )
        changes = payload.model_dump(exclude_unset=True, exclude={"version"})
        if "anagrafica_id" in changes and changes["anagrafica_id"]:
            self._valida_anagrafica(tenant_id, changes["anagrafica_id"])
        for field, value in changes.items():
            setattr(bolla, field, value)
        bolla.version += 1
        saved = self.repository.update(bolla)
        self.repository.session.commit()
        return BollaResponse.model_validate(saved)

    async def delete_bolla(self, tenant_id: str, bolla_id: str) -> None:
        """Cancella una bozza (solo stato bozza)."""
        bolla = self._get_or_404(tenant_id, bolla_id)
        self._assert_bozza(bolla, azione="cancellare")
        self.repository.delete(bolla)
        self.repository.session.commit()

    # ── Righe (solo bozza) ────────────────────────────────────────────────

    async def add_riga(
        self, tenant_id: str, bolla_id: str, payload: RigaCreateRequest
    ) -> BollaResponse:
        """Aggiunge una riga prendendo lo snapshot dei dati articolo."""
        bolla = self._get_or_404(tenant_id, bolla_id)
        self._assert_bozza(bolla)
        articolo = self.articolo_repository.get(tenant_id, payload.articolo_id)
        if articolo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Articolo non trovato nel tenant corrente.",
            )
        importo = (payload.quantita * articolo.prezzo_unitario).quantize(_CENT, ROUND_HALF_UP)
        ordine = (max((r.ordine for r in bolla.righe), default=0)) + 1
        # Append via collezione ORM: cascade insert al flush e collezione sempre in
        # sync (evita il bug del ricalcolo su righe stantie ricaricate da identity-map).
        bolla.righe.append(
            BollaRiga(
                id=str(uuid4()),
                articolo_id=articolo.id,
                codice_articolo=articolo.codice,
                descrizione=articolo.descrizione,
                unita_misura=articolo.unita_misura,
                quantita=payload.quantita,
                prezzo_unitario=articolo.prezzo_unitario,
                aliquota_iva=articolo.aliquota_iva,
                importo_riga=importo,
                ordine=ordine,
            )
        )
        return await self._ricalcola_e_salva(bolla)

    async def update_riga(
        self, tenant_id: str, bolla_id: str, riga_id: str, payload: RigaUpdateRequest
    ) -> BollaResponse:
        """Aggiorna la quantita' di una riga ricalcolando l'importo."""
        bolla = self._get_or_404(tenant_id, bolla_id)
        self._assert_bozza(bolla)
        riga = next((r for r in bolla.righe if r.id == riga_id), None)
        if riga is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Riga non trovata.")
        riga.quantita = payload.quantita
        riga.importo_riga = (payload.quantita * riga.prezzo_unitario).quantize(_CENT, ROUND_HALF_UP)
        return await self._ricalcola_e_salva(bolla)

    async def delete_riga(self, tenant_id: str, bolla_id: str, riga_id: str) -> BollaResponse:
        """Rimuove una riga e ricalcola i totali."""
        bolla = self._get_or_404(tenant_id, bolla_id)
        self._assert_bozza(bolla)
        riga = next((r for r in bolla.righe if r.id == riga_id), None)
        if riga is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Riga non trovata.")
        # Orphan removal: togliere dalla collezione cancella la riga al flush.
        bolla.righe.remove(riga)
        return await self._ricalcola_e_salva(bolla)

    # ── Transizioni di stato ──────────────────────────────────────────────

    async def emetti(self, tenant_id: str, bolla_id: str) -> BollaResponse:
        """Emette la bozza: consuma il numero dalla sequence e congela il documento."""
        bolla = self._get_or_404(tenant_id, bolla_id)
        if bolla.stato != STATO_BOZZA:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo una bozza puo' essere emessa.",
            )
        if not bolla.righe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossibile emettere una bolla senza righe.",
            )

        sequence = self.repository.lock_document_sequence(tenant_id, SEQUENCE_DDT)
        if sequence is None or not sequence.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Numerazione bolle non configurata per il tenant.",
            )
        numero = f"{sequence.prefix or ''}{sequence.next_number}"
        sequence.next_number += 1
        self.repository.session.add(sequence)

        bolla.numero = numero
        bolla.anno = datetime.now(UTC).year
        bolla.stato = STATO_EMESSA
        bolla.version += 1
        saved = self.repository.update(bolla)
        self.repository.session.commit()
        await self._notifica(
            tenant_id, EventTypes.BOLLA_EMESSA, {"bolla_id": saved.id, "numero": numero}
        )
        return BollaResponse.model_validate(saved)

    async def annulla(self, tenant_id: str, bolla_id: str) -> BollaResponse:
        """Annulla una bolla emessa (stato terminale, resta a registro)."""
        bolla = self._get_or_404(tenant_id, bolla_id)
        if bolla.stato != STATO_EMESSA:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo una bolla emessa puo' essere annullata.",
            )
        bolla.stato = STATO_ANNULLATA
        bolla.version += 1
        saved = self.repository.update(bolla)
        self.repository.session.commit()
        await self._notifica(
            tenant_id, EventTypes.BOLLA_ANNULLATA, {"bolla_id": saved.id, "numero": saved.numero}
        )
        return BollaResponse.model_validate(saved)

    # ── Helpers ───────────────────────────────────────────────────────────

    def _get_or_404(self, tenant_id: str, bolla_id: str) -> Bolla:
        record = self.repository.get(tenant_id, bolla_id)
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bolla non trovata.")
        return record

    def _assert_bozza(self, bolla: Bolla, azione: str = "modificare") -> None:
        if bolla.stato != STATO_BOZZA:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Impossibile {azione} una bolla in stato '{bolla.stato}'.",
            )

    def _valida_anagrafica(self, tenant_id: str, anagrafica_id: str) -> None:
        """Verifica che il destinatario appartenga al tenant corrente."""
        if self.anagrafica_repository.get(tenant_id, anagrafica_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Anagrafica destinatario non trovata nel tenant corrente.",
            )

    async def _ricalcola_e_salva(self, bolla: Bolla) -> BollaResponse:
        """Ricalcola i totali testata dalle righe (in-memory), salva e committa."""
        imponibile = Decimal("0")
        iva = Decimal("0")
        for riga in bolla.righe:
            imponibile += riga.importo_riga
            iva += (riga.importo_riga * riga.aliquota_iva / Decimal("100")).quantize(
                _CENT, ROUND_HALF_UP
            )
        bolla.totale_imponibile = imponibile.quantize(_CENT, ROUND_HALF_UP)
        bolla.totale_iva = iva.quantize(_CENT, ROUND_HALF_UP)
        bolla.totale = (bolla.totale_imponibile + bolla.totale_iva).quantize(_CENT, ROUND_HALF_UP)
        saved = self.repository.update(bolla)
        self.repository.session.commit()
        return BollaResponse.model_validate(saved)

    async def _notifica(self, tenant_id: str, event_type: str, payload: dict) -> None:
        """Invalida la cache KPI e pubblica l'evento bolla + kpi.updated sul bus."""
        if self.redis_client is not None:
            await invalidate_cache_key_best_effort(
                self.redis_client, build_tenant_dashboard_kpis_cache_key(tenant_id)
            )
        if self.event_publisher is not None:
            await self.event_publisher.publish_to_tenant(tenant_id, event_type, payload)
            await self.event_publisher.publish_to_tenant(
                tenant_id, EventTypes.KPI_UPDATED, {"tenant_id": tenant_id, "reason": event_type}
            )
