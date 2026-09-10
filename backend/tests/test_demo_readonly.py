"""Test del middleware che tiene la demo pubblica in sola lettura.

Il punto delicato non e' che il blocco funzioni, ma *quali* percorsi lo
scavalcano: un prefisso di troppo in _DEMO_EXEMPT_PREFIXES aprirebbe le
scritture su una demo pubblica senza che niente lo segnali.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings


@pytest.fixture
def demo_attiva(monkeypatch: pytest.MonkeyPatch) -> None:
    """Forza la modalita demo per la durata del test."""
    monkeypatch.setattr(settings, "demo_readonly", True)


def _e_blocco_demo(response) -> bool:
    """Indica se la risposta e' il 403 emesso dal middleware demo.

    Distingue dal 403 dei permessi, che ha un corpo diverso: senza questo
    controllo un test passerebbe anche quando la richiesta viene fermata per
    tutt'altra ragione.
    """
    if response.status_code != 403:
        return False
    return response.json().get("demo_readonly") is True


@pytest.mark.usefixtures("demo_attiva")
def test_scrittura_business_bloccata(client: TestClient) -> None:
    """Una POST su un modulo business viene fermata dal middleware."""
    response = client.post(f"{settings.api_v1_prefix}/articoli", json={})

    assert _e_blocco_demo(response)


@pytest.mark.usefixtures("demo_attiva")
def test_report_non_bloccato(client: TestClient) -> None:
    """La generazione report resta raggiungibile anche in demo.

    Il task valida il tenant e simula i batch senza persistere nulla, quindi
    non c'e' scrittura da proteggere. Senza credenziali la richiesta si ferma
    all'autenticazione, ed e' esattamente cio' che si vuole osservare: il
    middleware demo l'ha lasciata proseguire.
    """
    response = client.post(f"{settings.api_v1_prefix}/reports/generate", json={})

    assert not _e_blocco_demo(response)


@pytest.mark.usefixtures("demo_attiva")
def test_lettura_mai_bloccata(client: TestClient) -> None:
    """Le GET non passano dal blocco, qualunque sia il percorso."""
    response = client.get(f"{settings.api_v1_prefix}/articoli")

    assert not _e_blocco_demo(response)


def test_senza_demo_le_scritture_passano(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Con demo_readonly a false il middleware non interviene."""
    monkeypatch.setattr(settings, "demo_readonly", False)

    response = client.post(f"{settings.api_v1_prefix}/articoli", json={})

    assert not _e_blocco_demo(response)
