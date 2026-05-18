"""Utility condivise per cache JSON e chiavi Redis tenant-aware."""

import logging
from collections.abc import Awaitable, Callable

from pydantic import BaseModel
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


def build_tenant_dashboard_kpis_cache_key(tenant_id: str) -> str:
    """Restituisce la chiave Redis isolata per i KPI dashboard di un tenant."""
    return f"tenant:{tenant_id}:dashboard:kpis"


async def get_or_set_model_cache[TModel: BaseModel](
    redis_client: Redis,
    key: str,
    ttl_seconds: int,
    model_class: type[TModel],
    loader: Callable[[], Awaitable[TModel]],
) -> TModel:
    """Legge un modello Pydantic da Redis o lo calcola e salva con TTL."""
    cached_payload = await redis_client.get(key)
    if cached_payload:
        return model_class.model_validate_json(cached_payload)

    model = await loader()
    await redis_client.set(key, model.model_dump_json(), ex=ttl_seconds)
    return model


async def invalidate_cache_key(redis_client: Redis, key: str) -> bool:
    """Elimina una singola chiave di cache e indica se esisteva."""
    deleted = await redis_client.delete(key)
    return bool(deleted)


async def invalidate_cache_key_best_effort(redis_client: Redis, key: str) -> bool:
    """Prova a invalidare una chiave senza interrompere il flusso applicativo."""
    try:
        return await invalidate_cache_key(redis_client, key)
    except Exception:
        logger.exception("Invalidazione cache fallita per la chiave Redis '%s'.", key)
        return False
