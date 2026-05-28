"""Servizio applicativo per il modulo Articoli."""

from fastapi import HTTPException, status
from redis.asyncio import Redis

from app.core.cache import (
    build_tenant_dashboard_kpis_cache_key,
    invalidate_cache_key_best_effort,
)
from app.models.core.articolo import Articolo
from app.repositories.core.articolo_repository import ArticoloRepository
from app.repositories.core.categoria_articolo_repository import CategoriaArticoloRepository
from app.schemas.articoli.requests import (
    ArticoloCreateRequest,
    ArticoloListParams,
    ArticoloUpdateRequest,
)
from app.schemas.articoli.responses import ArticoloListResponse, ArticoloResponse
from app.schemas.events.sse import EventTypes
from app.services.events.event_publisher import EventPublisher


class ArticoloService:
    """Casi d'uso del modulo Articoli, tenant-aware con optimistic locking ed eventi."""

    def __init__(
        self,
        repository: ArticoloRepository,
        categoria_repository: CategoriaArticoloRepository,
        redis_client: Redis | None = None,
        event_publisher: EventPublisher | None = None,
    ) -> None:
        self.repository = repository
        self.categoria_repository = categoria_repository
        self.redis_client = redis_client
        self.event_publisher = event_publisher

    def list_articoli(self, tenant_id: str, params: ArticoloListParams) -> ArticoloListResponse:
        """Restituisce la lista paginata degli articoli del tenant."""
        items, total = self.repository.list(
            tenant_id,
            categoria_id=params.categoria_id,
            is_active=params.is_active,
            q=params.q,
            skip=params.skip,
            limit=params.limit,
        )
        return ArticoloListResponse(
            items=[ArticoloResponse.model_validate(a) for a in items],
            total=total,
            skip=params.skip,
            limit=params.limit,
        )

    def get_articolo(self, tenant_id: str, articolo_id: str) -> ArticoloResponse:
        """Restituisce un singolo articolo del tenant."""
        return ArticoloResponse.model_validate(self._get_or_404(tenant_id, articolo_id))

    async def create_articolo(
        self, tenant_id: str, payload: ArticoloCreateRequest
    ) -> ArticoloResponse:
        """Crea un articolo validando codice univoco e categoria nel tenant."""
        if self.repository.get_by_codice(tenant_id, payload.codice) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esiste gia un articolo con questo codice.",
            )
        self._valida_categoria_nel_tenant(tenant_id, payload.categoria_id)

        articolo = Articolo(
            tenant_id=tenant_id,
            codice=payload.codice,
            categoria_id=payload.categoria_id,
            descrizione=payload.descrizione,
            unita_misura=payload.unita_misura,
            prezzo_unitario=payload.prezzo_unitario,
            aliquota_iva=payload.aliquota_iva,
            giacenza=payload.giacenza,
            codice_ean=payload.codice_ean,
            note=payload.note,
        )
        saved = self.repository.create(articolo)
        self.repository.session.commit()
        await self._notifica_mutazione(
            tenant_id,
            EventTypes.ARTICOLO_CREATED,
            {"articolo_id": saved.id, "codice": saved.codice},
        )
        return ArticoloResponse.model_validate(saved)

    async def update_articolo(
        self, tenant_id: str, articolo_id: str, payload: ArticoloUpdateRequest
    ) -> ArticoloResponse:
        """Aggiorna un articolo con controllo optimistic locking sulla version."""
        record = self._get_or_404(tenant_id, articolo_id)

        if record.version != payload.version:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Articolo modificato da un altro utente, ricarica la pagina.",
            )

        changes = payload.model_dump(exclude_unset=True, exclude={"version"})

        nuovo_codice = changes.get("codice")
        if nuovo_codice and nuovo_codice != record.codice:
            existing = self.repository.get_by_codice(tenant_id, nuovo_codice)
            if existing is not None and existing.id != record.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Esiste gia un articolo con questo codice.",
                )

        if "categoria_id" in changes:
            self._valida_categoria_nel_tenant(tenant_id, changes["categoria_id"])

        for field, value in changes.items():
            setattr(record, field, value)
        record.version += 1
        saved = self.repository.update(record)
        self.repository.session.commit()
        await self._notifica_mutazione(
            tenant_id,
            EventTypes.ARTICOLO_UPDATED,
            {"articolo_id": saved.id, "codice": saved.codice},
        )
        return ArticoloResponse.model_validate(saved)

    async def delete_articolo(self, tenant_id: str, articolo_id: str) -> None:
        """Soft delete: imposta is_active = False."""
        record = self._get_or_404(tenant_id, articolo_id)
        record.is_active = False
        record.version += 1
        self.repository.update(record)
        self.repository.session.commit()
        await self._notifica_mutazione(
            tenant_id, EventTypes.ARTICOLO_DEACTIVATED, {"articolo_id": record.id}
        )

    # ── Helpers ────────────────────────────────────────────────────────────

    def _get_or_404(self, tenant_id: str, articolo_id: str) -> Articolo:
        record = self.repository.get(tenant_id, articolo_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Articolo non trovato.",
            )
        return record

    def _valida_categoria_nel_tenant(self, tenant_id: str, categoria_id: str | None) -> None:
        """Verifica che la categoria appartenga al tenant corrente.

        Punto tenant-critico: senza questo controllo un client potrebbe linkare
        la categoria di un altro tenant passando un id arbitrario.
        """
        if categoria_id is None:
            return
        if self.categoria_repository.get(tenant_id, categoria_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria non trovata nel tenant corrente.",
            )

    async def _notifica_mutazione(self, tenant_id: str, event_type: str, payload: dict) -> None:
        """Invalida la cache KPI e pubblica l'evento articolo + kpi.updated sul bus."""
        if self.redis_client is not None:
            cache_key = build_tenant_dashboard_kpis_cache_key(tenant_id)
            await invalidate_cache_key_best_effort(self.redis_client, cache_key)
        if self.event_publisher is not None:
            await self.event_publisher.publish_to_tenant(tenant_id, event_type, payload)
            await self.event_publisher.publish_to_tenant(
                tenant_id, EventTypes.KPI_UPDATED, {"tenant_id": tenant_id, "reason": event_type}
            )
