"""Test dei health endpoint e della propagazione request id."""

from fastapi import status

import app.main as main_module
from app.core.config import settings


def test_health_live_restituisce_ok_e_request_id(client) -> None:
    """La liveness deve rispondere 200 e restituire il request id."""
    response = client.get("/health/live")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}
    assert response.headers[settings.request_id_header_name]


def test_health_ready_restituisce_ok_quando_db_e_redis_sono_disponibili(
    client,
    monkeypatch,
) -> None:
    """La readiness deve confermare che database e Redis siano raggiungibili."""
    monkeypatch.setattr(main_module, "_check_database", lambda: {"status": "ok"})

    response = client.get("/health/ready")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "status": "ok",
        "checks": {
            "database": {"status": "ok"},
            "redis": {"status": "ok"},
        },
    }


def test_health_ready_restituisce_503_quando_il_database_non_e_pronto(
    client,
    monkeypatch,
) -> None:
    """La readiness deve degradare se il database non risponde, senza esporre l'errore."""

    def broken_database_check() -> dict[str, str]:
        raise RuntimeError("database down")

    monkeypatch.setattr(main_module, "_check_database", broken_database_check)

    response = client.get("/health/ready")

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["database"] == {"status": "error"}
    # L'endpoint e' pubblico: il testo dell'eccezione non deve uscire (17abebd).
    assert "database down" not in response.text
    assert body["checks"]["redis"]["status"] == "ok"
