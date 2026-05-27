"""Punto di ingresso dell'applicazione FastAPI."""

import logging
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.db import engine
from app.core.logging import configure_logging
from app.core.redis import create_redis_client
from app.core.request_id import reset_request_id, set_request_id

configure_logging()
logger = logging.getLogger("app.http")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inizializza e chiude il client Redis condiviso dell'applicazione."""
    redis_client = create_redis_client()
    await redis_client.ping()
    app.state.redis = redis_client
    try:
        yield
    finally:
        await redis_client.aclose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    openapi_url=None if settings.is_production_like else f"{settings.api_v1_prefix}/openapi.json",
    docs_url=None if settings.is_production_like else "/docs",
    redoc_url=None if settings.is_production_like else "/redoc",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """Propaga un request id e registra il risultato di ogni richiesta HTTP."""
    request_id = request.headers.get(settings.request_id_header_name) or str(uuid4())
    request.state.request_id = request_id
    token = set_request_id(request_id)
    started_at = perf_counter()
    client_ip = request.client.host if request.client is not None else "unknown"

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        logger.exception(
            "Richiesta HTTP terminata con errore non gestito.",
            extra={
                "http_method": request.method,
                "http_path": request.url.path,
                "client_ip": client_ip,
                "duration_ms": duration_ms,
            },
        )
        raise
    else:
        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        response.headers[settings.request_id_header_name] = request_id
        logger.info(
            "Richiesta HTTP completata.",
            extra={
                "http_method": request.method,
                "http_path": request.url.path,
                "http_status_code": response.status_code,
                "client_ip": client_ip,
                "duration_ms": duration_ms,
            },
        )
        return response
    finally:
        reset_request_id(token)


def _check_database() -> dict[str, str]:
    """Verifica minima della connettivita al database."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"status": "ok"}


async def _check_redis(request: Request) -> dict[str, str]:
    """Verifica minima della connettivita a Redis."""
    await request.app.state.redis.ping()
    return {"status": "ok"}


@app.get("/health", tags=["health"])
async def healthcheck() -> dict[str, str]:
    """Alias minimale di liveness per compatibilita retroattiva."""
    return {"status": "ok"}


@app.get("/health/live", tags=["health"])
async def liveness_check() -> dict[str, str]:
    """Conferma che il processo web sia vivo."""
    return {"status": "ok"}


@app.get("/health/ready", tags=["health"])
async def readiness_check(request: Request) -> JSONResponse:
    """Verifica che web, database e Redis siano pronti a servire traffico."""
    checks: dict[str, dict[str, str]] = {}
    is_ready = True

    try:
        checks["database"] = _check_database()
    except Exception:
        is_ready = False
        checks["database"] = {"status": "error"}

    try:
        checks["redis"] = await _check_redis(request)
    except Exception:
        is_ready = False
        checks["redis"] = {"status": "error"}

    payload = {
        "status": "ok" if is_ready else "degraded",
        "checks": checks,
    }
    return JSONResponse(
        status_code=status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=payload,
    )
