"""Client Redis dedicato alle connessioni pub/sub degli eventi applicativi."""

from redis.asyncio import Redis

from app.core.config import settings


def create_pubsub_redis_client() -> Redis:
    """Crea un client Redis fresco per un subscriber pub/sub (db 3).

    Ogni stream SSE richiede la propria connessione dedicata: una volta
    in modalita pub/sub, la connessione non puo piu eseguire comandi normali.
    """
    return Redis.from_url(
        settings.redis_pubsub_url,
        encoding="utf-8",
        decode_responses=True,
    )
