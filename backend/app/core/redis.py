"""Bootstrap e dependency del client Redis asincrono."""

from typing import cast

from fastapi import Request
from redis.asyncio import Redis

from app.core.config import settings


def create_redis_client() -> Redis:
    """Crea il client Redis asincrono condiviso dall'app FastAPI."""
    return Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )


def get_redis_client(request: Request) -> Redis:
    """Restituisce il client Redis salvato nello stato dell'applicazione."""
    return cast(Redis, request.app.state.redis)
