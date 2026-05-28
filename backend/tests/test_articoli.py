"""Test unit dei service Articoli e Categorie (tenant scoping, optimistic lock)."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, status

from app.models.core.articolo import Articolo
from app.models.core.categoria_articolo import CategoriaArticolo
from app.schemas.articoli.requests import (
    ArticoloCreateRequest,
    ArticoloUpdateRequest,
    CategoriaCreateRequest,
)
from app.services.articoli.articolo_service import ArticoloService
from app.services.articoli.categoria_service import CategoriaService

TENANT_A = "11111111-1111-4111-8111-111111111111"
TENANT_B = "22222222-2222-4222-8222-222222222222"


def _make_articolo(
    *, tenant_id: str = TENANT_A, articolo_id: str = "art-1", version: int = 1
) -> Articolo:
    now = datetime.now(UTC)
    art = Articolo(
        tenant_id=tenant_id,
        codice="PAV-001",
        categoria_id=None,
        descrizione="Gres 60x60",
        unita_misura="m²",
        prezzo_unitario=Decimal("18.50"),
        aliquota_iva=Decimal("22.00"),
        giacenza=Decimal("100.000"),
        codice_ean=None,
        note=None,
    )
    art.id = articolo_id
    art.version = version
    art.is_active = True
    art.created_at = now
    art.updated_at = now
    return art


def _make_categoria(*, tenant_id: str = TENANT_A, categoria_id: str = "cat-1") -> CategoriaArticolo:
    now = datetime.now(UTC)
    cat = CategoriaArticolo(tenant_id=tenant_id, nome="Pavimenti", descrizione=None)
    cat.id = categoria_id
    cat.is_active = True
    cat.created_at = now
    cat.updated_at = now
    return cat


def _simula_flush(articolo: Articolo) -> Articolo:
    """Simula il flush+refresh del repository popolando i default ORM."""
    now = datetime.now(UTC)
    if articolo.id is None:
        articolo.id = "art-nuovo"
    if articolo.is_active is None:
        articolo.is_active = True
    if articolo.version is None:
        articolo.version = 1
    if articolo.created_at is None:
        articolo.created_at = now
    if articolo.updated_at is None:
        articolo.updated_at = now
    return articolo


def _articolo_service(*, articolo=None, categoria=None, codice_existing=None) -> ArticoloService:
    repo = MagicMock()
    repo.get = MagicMock(return_value=articolo)
    repo.get_by_codice = MagicMock(return_value=codice_existing)
    repo.create = MagicMock(side_effect=_simula_flush)
    repo.update = MagicMock(side_effect=_simula_flush)

    cat_repo = MagicMock()
    cat_repo.get = MagicMock(return_value=categoria)

    redis_client = MagicMock()
    redis_client.delete = AsyncMock()
    event_publisher = MagicMock()
    event_publisher.publish_to_tenant = AsyncMock()

    return ArticoloService(
        repo, cat_repo, redis_client=redis_client, event_publisher=event_publisher
    )


# ── Tenant scoping ───────────────────────────────────────────────────────────


def test_get_articolo_di_altro_tenant_da_404() -> None:
    """Il repository scoped ritorna None per un id di un altro tenant → 404."""
    service = _articolo_service(articolo=None)
    with pytest.raises(HTTPException) as exc:
        service.get_articolo(TENANT_B, "art-di-tenant-A")
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_create_usa_tenant_dalla_sessione_non_dal_payload() -> None:
    """Il tenant_id dell'articolo creato proviene dal parametro, non dal payload."""
    service = _articolo_service(articolo=None, categoria=None, codice_existing=None)
    payload = ArticoloCreateRequest(codice="NEW-1", descrizione="Nuovo", unita_misura="pz")
    result = asyncio.run(service.create_articolo(TENANT_A, payload))
    assert result.tenant_id == TENANT_A


# ── Categoria cross-tenant ───────────────────────────────────────────────────


def test_create_con_categoria_di_altro_tenant_da_404() -> None:
    """Se categoria_id non esiste nel tenant corrente, la creazione fallisce con 404."""
    # cat_repo.get ritorna None → categoria non nel tenant
    service = _articolo_service(articolo=None, categoria=None, codice_existing=None)
    payload = ArticoloCreateRequest(
        codice="NEW-2", descrizione="Nuovo", categoria_id="cat-di-altro-tenant"
    )
    with pytest.raises(HTTPException) as exc:
        asyncio.run(service.create_articolo(TENANT_A, payload))
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Categoria" in exc.value.detail


def test_create_con_categoria_valida_nel_tenant_passa() -> None:
    """Categoria appartenente al tenant → creazione consentita."""
    categoria = _make_categoria(tenant_id=TENANT_A, categoria_id="cat-1")
    service = _articolo_service(articolo=None, categoria=categoria, codice_existing=None)
    payload = ArticoloCreateRequest(codice="NEW-3", descrizione="Nuovo", categoria_id="cat-1")
    result = asyncio.run(service.create_articolo(TENANT_A, payload))
    assert result.categoria_id == "cat-1"


# ── Codice univoco ───────────────────────────────────────────────────────────


def test_create_con_codice_duplicato_da_409() -> None:
    """Codice gia presente nel tenant → 409."""
    esistente = _make_articolo()
    service = _articolo_service(articolo=None, codice_existing=esistente)
    payload = ArticoloCreateRequest(codice="PAV-001", descrizione="Dup")
    with pytest.raises(HTTPException) as exc:
        asyncio.run(service.create_articolo(TENANT_A, payload))
    assert exc.value.status_code == status.HTTP_409_CONFLICT


# ── Optimistic locking ───────────────────────────────────────────────────────


def test_update_con_version_corretta_incrementa_version() -> None:
    """Version coincidente → update applicato e version incrementata."""
    articolo = _make_articolo(version=3)
    service = _articolo_service(articolo=articolo)
    payload = ArticoloUpdateRequest(version=3, descrizione="Aggiornato")
    result = asyncio.run(service.update_articolo(TENANT_A, "art-1", payload))
    assert result.version == 4
    assert result.descrizione == "Aggiornato"


def test_update_con_version_stale_da_409() -> None:
    """Version divergente (record modificato da altri) → 409, nessuna modifica."""
    articolo = _make_articolo(version=5)
    service = _articolo_service(articolo=articolo)
    payload = ArticoloUpdateRequest(version=3, descrizione="Tentativo stale")
    with pytest.raises(HTTPException) as exc:
        asyncio.run(service.update_articolo(TENANT_A, "art-1", payload))
    assert exc.value.status_code == status.HTTP_409_CONFLICT


# ── Eventi ───────────────────────────────────────────────────────────────────


def test_create_pubblica_evento_e_invalida_cache() -> None:
    """La creazione pubblica articolo.created + kpi.updated e invalida la cache."""
    service = _articolo_service(articolo=None, codice_existing=None)
    payload = ArticoloCreateRequest(codice="EV-1", descrizione="Evento")
    asyncio.run(service.create_articolo(TENANT_A, payload))
    # due publish: articolo.created + kpi.updated
    assert service.event_publisher.publish_to_tenant.await_count == 2
    service.redis_client.delete.assert_awaited()


# ── Categorie: delete bloccato se in uso ─────────────────────────────────────


def _categoria_service(
    *, categoria=None, count_attivi: int = 0, nome_existing=None
) -> CategoriaService:
    repo = MagicMock()
    repo.get = MagicMock(return_value=categoria)
    repo.get_by_nome = MagicMock(return_value=nome_existing)
    repo.count_articoli_attivi = MagicMock(return_value=count_attivi)
    repo.create = MagicMock(side_effect=lambda c: c)
    repo.update = MagicMock(side_effect=lambda c: c)
    return CategoriaService(repo)


def test_delete_categoria_con_articoli_attivi_da_409() -> None:
    """Disattivare una categoria in uso da articoli attivi → 409."""
    categoria = _make_categoria()
    service = _categoria_service(categoria=categoria, count_attivi=4)
    with pytest.raises(HTTPException) as exc:
        service.delete_categoria(TENANT_A, "cat-1")
    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert "4" in exc.value.detail


def test_delete_categoria_libera_disattiva() -> None:
    """Categoria senza articoli attivi → soft delete consentito."""
    categoria = _make_categoria()
    service = _categoria_service(categoria=categoria, count_attivi=0)
    service.delete_categoria(TENANT_A, "cat-1")
    assert categoria.is_active is False


def test_create_categoria_nome_duplicato_da_409() -> None:
    """Nome categoria gia presente nel tenant → 409."""
    esistente = _make_categoria()
    service = _categoria_service(nome_existing=esistente)
    with pytest.raises(HTTPException) as exc:
        service.create_categoria(TENANT_A, CategoriaCreateRequest(nome="Pavimenti"))
    assert exc.value.status_code == status.HTTP_409_CONFLICT
