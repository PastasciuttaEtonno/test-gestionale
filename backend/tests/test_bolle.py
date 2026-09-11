"""Test unit del BollaService: lifecycle, snapshot, numerazione, immutabilita'."""

from __future__ import annotations

import asyncio
from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, status

from app.models.core.articolo import Articolo
from app.models.core.bolla import Bolla
from app.models.core.bolla_riga import BollaRiga
from app.models.core.tenant_document_sequence import TenantDocumentSequence
from app.schemas.bolle.requests import (
    BollaCreateRequest,
    BollaUpdateRequest,
    RigaCreateRequest,
    RigaUpdateRequest,
)
from app.services.bolle.bolla_service import BollaService

TENANT_A = "11111111-1111-4111-8111-111111111111"


def _make_bolla(*, stato: str = "bozza", version: int = 1, righe: list | None = None) -> Bolla:
    now = datetime.now(UTC)
    b = Bolla(
        tenant_id=TENANT_A,
        stato=stato,
        data_documento=date(2026, 5, 28),
        anagrafica_id="anag-1",
        causale_trasporto="vendita",
    )
    b.id = "bolla-1"
    b.numero = "BL4441" if stato != "bozza" else None
    b.anno = 2026 if stato != "bozza" else None
    b.aspetto_beni = None
    b.num_colli = None
    b.peso_kg = None
    b.trasporto_a_cura = None
    b.vettore = None
    b.note = None
    b.totale_imponibile = Decimal("0")
    b.totale_iva = Decimal("0")
    b.totale = Decimal("0")
    b.is_active = True
    b.version = version
    b.created_at = now
    b.updated_at = now
    b.righe = righe if righe is not None else []
    return b


def _make_articolo(*, giacenza: Decimal = Decimal("100")) -> Articolo:
    a = Articolo(
        tenant_id=TENANT_A,
        codice="PAV-GRES-6060-GR",
        descrizione="Gres porcellanato 60x60 grigio",
        unita_misura="m²",
        prezzo_unitario=Decimal("18.5000"),
        aliquota_iva=Decimal("22.00"),
        giacenza=giacenza,
    )
    a.id = "art-1"
    a.version = 1
    return a


def _make_riga(*, articolo_id: str | None, quantita: str, ordine: int = 1) -> BollaRiga:
    riga = BollaRiga(
        bolla_id="bolla-1",
        articolo_id=articolo_id,
        codice_articolo="PAV-GRES-6060-GR",
        descrizione="Gres porcellanato 60x60 grigio",
        unita_misura="m²",
        quantita=Decimal(quantita),
        prezzo_unitario=Decimal("18.5000"),
        aliquota_iva=Decimal("22.00"),
        importo_riga=Decimal("0.00"),
        ordine=ordine,
    )
    riga.id = f"riga-{ordine}"
    return riga


def _make_sequence() -> TenantDocumentSequence:
    seq = TenantDocumentSequence(
        tenant_id=TENANT_A,
        sequence_code="delivery_note_italy",
        name="Bolle Italia",
        prefix="BL",
        next_number=4442,
        reset_policy="continuous",
    )
    seq.is_active = True
    return seq


def _simula_flush_bolla(b: Bolla) -> Bolla:
    """Popola i default ORM che in produzione arrivano da flush+refresh."""
    now = datetime.now(UTC)
    if b.id is None:
        b.id = "bolla-nuova"
    if b.version is None:
        b.version = 1
    if b.is_active is None:
        b.is_active = True
    for attr in ("totale_imponibile", "totale_iva", "totale"):
        if getattr(b, attr, None) is None:
            setattr(b, attr, Decimal("0"))
    if b.created_at is None:
        b.created_at = now
    if b.updated_at is None:
        b.updated_at = now
    if not hasattr(b, "righe") or b.righe is None:
        b.righe = []
    return b


def _make_service(
    *,
    bolla: Bolla | None = None,
    articolo: Articolo | None = None,
    anagrafica_exists: bool = True,
    sequence: TenantDocumentSequence | None = None,
) -> BollaService:
    repo = MagicMock()
    repo.session = MagicMock()
    repo.get = MagicMock(return_value=bolla)
    repo.create = MagicMock(side_effect=_simula_flush_bolla)
    repo.update = MagicMock(side_effect=lambda b: b)
    repo.delete = MagicMock()
    repo.lock_document_sequence = MagicMock(return_value=sequence)

    _riga_counter = {"n": 0}

    def _add_riga(riga):
        if riga.id is None:
            _riga_counter["n"] += 1
            riga.id = f"riga-{_riga_counter['n']}"
        if bolla is not None:
            bolla.righe.append(riga)
        return riga

    repo.add_riga = MagicMock(side_effect=_add_riga)

    def _get_riga(_bid, rid):
        return next((r for r in (bolla.righe if bolla else []) if r.id == rid), None)

    repo.get_riga = MagicMock(side_effect=_get_riga)

    def _del_riga(riga):
        if bolla is not None:
            bolla.righe = [r for r in bolla.righe if r.id != riga.id]

    repo.delete_riga = MagicMock(side_effect=_del_riga)

    anag_repo = MagicMock()
    anag_repo.get = MagicMock(return_value=(object() if anagrafica_exists else None))

    art_repo = MagicMock()
    art_repo.get = MagicMock(return_value=articolo)
    magazzino = [articolo] if articolo is not None else []
    art_repo.lock_for_update = MagicMock(
        side_effect=lambda _tid, ids: [a for a in magazzino if a.id in ids]
    )

    redis = MagicMock()
    publisher = MagicMock()
    publisher.publish_to_tenant = AsyncMock()

    return BollaService(repo, anag_repo, art_repo, redis_client=redis, event_publisher=publisher)


# ── Creazione / tenant ────────────────────────────────────────────────────


def test_create_bolla_con_anagrafica_di_altro_tenant_da_404() -> None:
    service = _make_service(bolla=None, anagrafica_exists=False)
    payload = BollaCreateRequest(anagrafica_id="anag-altrui", data_documento=date(2026, 5, 28))
    with pytest.raises(HTTPException) as exc:
        asyncio.run(service.create_bolla(TENANT_A, payload))
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_create_bolla_nasce_in_bozza_senza_numero() -> None:
    service = _make_service(bolla=None, anagrafica_exists=True)
    payload = BollaCreateRequest(anagrafica_id="anag-1", data_documento=date(2026, 5, 28))
    result = asyncio.run(service.create_bolla(TENANT_A, payload))
    assert result.stato == "bozza"
    assert result.numero is None


# ── Righe: snapshot + totali ────────────────────────────────────────────────


def test_add_riga_snapshotta_articolo_e_ricalcola_totali() -> None:
    bolla = _make_bolla(stato="bozza")
    service = _make_service(bolla=bolla, articolo=_make_articolo())
    result = asyncio.run(
        service.add_riga(
            TENANT_A, "bolla-1", RigaCreateRequest(articolo_id="art-1", quantita=Decimal("50"))
        )
    )
    # snapshot
    riga = bolla.righe[0]
    assert riga.codice_articolo == "PAV-GRES-6060-GR"
    assert riga.prezzo_unitario == Decimal("18.5000")
    assert riga.importo_riga == Decimal("925.00")
    # totali ricalcolati: 925 imponibile, 22% = 203.50 iva, 1128.50 totale
    assert result.totale_imponibile == Decimal("925.00")
    assert result.totale_iva == Decimal("203.50")
    assert result.totale == Decimal("1128.50")


def test_add_riga_con_articolo_di_altro_tenant_da_404() -> None:
    bolla = _make_bolla(stato="bozza")
    service = _make_service(bolla=bolla, articolo=None)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            service.add_riga(
                TENANT_A, "bolla-1", RigaCreateRequest(articolo_id="x", quantita=Decimal("1"))
            )
        )
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_add_riga_su_bolla_emessa_da_409() -> None:
    bolla = _make_bolla(stato="emessa")
    service = _make_service(bolla=bolla, articolo=_make_articolo())
    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            service.add_riga(
                TENANT_A, "bolla-1", RigaCreateRequest(articolo_id="art-1", quantita=Decimal("1"))
            )
        )
    assert exc.value.status_code == status.HTTP_409_CONFLICT


def test_update_riga_ricalcola_importo() -> None:
    riga = BollaRiga(
        bolla_id="bolla-1",
        articolo_id="art-1",
        codice_articolo="X",
        descrizione="Y",
        unita_misura="m²",
        quantita=Decimal("10"),
        prezzo_unitario=Decimal("18.5000"),
        aliquota_iva=Decimal("22.00"),
        importo_riga=Decimal("185.00"),
        ordine=1,
    )
    riga.id = "riga-1"
    bolla = _make_bolla(stato="bozza", righe=[riga])
    service = _make_service(bolla=bolla)
    result = asyncio.run(
        service.update_riga(
            TENANT_A, "bolla-1", "riga-1", RigaUpdateRequest(quantita=Decimal("20"))
        )
    )
    assert riga.importo_riga == Decimal("370.00")
    assert result.totale_imponibile == Decimal("370.00")


# ── Emissione: numerazione ──────────────────────────────────────────────────


def test_emetti_consuma_numero_e_passa_a_emessa() -> None:
    riga = BollaRiga(
        bolla_id="bolla-1",
        descrizione="X",
        unita_misura="pz",
        quantita=Decimal("1"),
        prezzo_unitario=Decimal("10"),
        aliquota_iva=Decimal("22.00"),
        importo_riga=Decimal("10.00"),
        ordine=1,
    )
    riga.id = "riga-1"
    bolla = _make_bolla(stato="bozza", righe=[riga])
    seq = TenantDocumentSequence(
        tenant_id=TENANT_A,
        sequence_code="delivery_note_italy",
        name="Bolle Italia",
        prefix="BL",
        next_number=4442,
        reset_policy="continuous",
    )
    seq.is_active = True
    service = _make_service(bolla=bolla, sequence=seq)
    result = asyncio.run(service.emetti(TENANT_A, "bolla-1"))
    assert result.stato == "emessa"
    assert result.numero == "BL4442"
    assert seq.next_number == 4443  # incrementata


def test_emetti_senza_righe_da_400() -> None:
    bolla = _make_bolla(stato="bozza", righe=[])
    service = _make_service(bolla=bolla, sequence=None)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(service.emetti(TENANT_A, "bolla-1"))
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


def test_emetti_bolla_gia_emessa_da_409() -> None:
    bolla = _make_bolla(stato="emessa")
    service = _make_service(bolla=bolla)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(service.emetti(TENANT_A, "bolla-1"))
    assert exc.value.status_code == status.HTTP_409_CONFLICT


# ── Magazzino: scarico all'emissione, ricarico all'annullamento ─────────────


def test_emetti_scarica_la_giacenza_sommando_le_righe_dello_stesso_articolo() -> None:
    articolo = _make_articolo(giacenza=Decimal("100"))
    righe = [
        _make_riga(articolo_id="art-1", quantita="30", ordine=1),
        _make_riga(articolo_id="art-1", quantita="20", ordine=2),
    ]
    bolla = _make_bolla(stato="bozza", righe=righe)
    service = _make_service(bolla=bolla, articolo=articolo, sequence=_make_sequence())

    asyncio.run(service.emetti(TENANT_A, "bolla-1"))

    assert articolo.giacenza == Decimal("50")
    assert bolla.giacenza_scaricata is True
    # Una scheda articolo aperta prima dell'emissione ora riceve un 409.
    assert articolo.version == 2


def test_emetti_con_giacenza_insufficiente_resta_in_bozza_e_non_consuma_il_numero() -> None:
    articolo = _make_articolo(giacenza=Decimal("10"))
    bolla = _make_bolla(stato="bozza", righe=[_make_riga(articolo_id="art-1", quantita="25")])
    seq = _make_sequence()
    service = _make_service(bolla=bolla, articolo=articolo, sequence=seq)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(service.emetti(TENANT_A, "bolla-1"))

    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert "PAV-GRES-6060-GR (disponibili 10 m², richiesti 25)" in exc.value.detail
    assert articolo.giacenza == Decimal("10")
    assert bolla.stato == "bozza"
    assert seq.next_number == 4442


def test_annulla_rimette_in_giacenza_le_quantita() -> None:
    articolo = _make_articolo(giacenza=Decimal("50"))
    bolla = _make_bolla(stato="emessa", righe=[_make_riga(articolo_id="art-1", quantita="30")])
    bolla.giacenza_scaricata = True
    service = _make_service(bolla=bolla, articolo=articolo)

    asyncio.run(service.annulla(TENANT_A, "bolla-1"))

    assert articolo.giacenza == Decimal("80")
    assert bolla.giacenza_scaricata is False


def test_annulla_bolla_emessa_prima_dello_scarico_non_tocca_la_giacenza() -> None:
    articolo = _make_articolo(giacenza=Decimal("50"))
    bolla = _make_bolla(stato="emessa", righe=[_make_riga(articolo_id="art-1", quantita="30")])
    bolla.giacenza_scaricata = False
    service = _make_service(bolla=bolla, articolo=articolo)

    result = asyncio.run(service.annulla(TENANT_A, "bolla-1"))

    assert result.stato == "annullata"
    assert articolo.giacenza == Decimal("50")


# ── Annullamento ────────────────────────────────────────────────────────────


def test_annulla_bolla_emessa() -> None:
    bolla = _make_bolla(stato="emessa")
    service = _make_service(bolla=bolla)
    result = asyncio.run(service.annulla(TENANT_A, "bolla-1"))
    assert result.stato == "annullata"


def test_annulla_bozza_da_409() -> None:
    bolla = _make_bolla(stato="bozza")
    service = _make_service(bolla=bolla)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(service.annulla(TENANT_A, "bolla-1"))
    assert exc.value.status_code == status.HTTP_409_CONFLICT


# ── Optimistic locking testata ──────────────────────────────────────────────


def test_update_bolla_version_stale_da_409() -> None:
    bolla = _make_bolla(stato="bozza", version=5)
    service = _make_service(bolla=bolla)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            service.update_bolla(TENANT_A, "bolla-1", BollaUpdateRequest(version=3, note="x"))
        )
    assert exc.value.status_code == status.HTTP_409_CONFLICT


def test_update_bolla_version_corretta_incrementa() -> None:
    bolla = _make_bolla(stato="bozza", version=3)
    service = _make_service(bolla=bolla)
    result = asyncio.run(
        service.update_bolla(TENANT_A, "bolla-1", BollaUpdateRequest(version=3, note="agg"))
    )
    assert result.version == 4
    assert result.note == "agg"


# ── Cancellazione bozza ─────────────────────────────────────────────────────


def test_delete_bolla_emessa_da_409() -> None:
    bolla = _make_bolla(stato="emessa")
    service = _make_service(bolla=bolla)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(service.delete_bolla(TENANT_A, "bolla-1"))
    assert exc.value.status_code == status.HTTP_409_CONFLICT
