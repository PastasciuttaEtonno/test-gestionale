"""Fixture condivise per i test backend."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app


class FakeRedis:
    """Client Redis minimale per test senza dipendenze esterne."""

    async def ping(self) -> bool:
        """Simula una risposta positiva di healthcheck Redis."""
        return True

    async def aclose(self) -> None:
        """Simula la chiusura del client Redis."""


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    """Restituisce un TestClient con Redis finto e dependency override pulite."""
    monkeypatch.setattr(main_module, "create_redis_client", lambda: FakeRedis())
    app.dependency_overrides.clear()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
