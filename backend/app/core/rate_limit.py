"""Dependency FastAPI per rate limiting basato su Redis."""

from collections.abc import Callable
from time import time

from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

from app.api.deps.auth import get_optional_current_user
from app.core.redis import get_redis_client
from app.schemas.auth.responses import CurrentUserResponse


def rate_limit_dependency(
    limit: int,
    window_seconds: int,
    scope: str,
) -> Callable:
    """Restituisce una dependency che applica rate limiting fixed-window."""

    async def dependency(
        request: Request,
        redis_client: Redis = Depends(get_redis_client),
        current_user: CurrentUserResponse | None = Depends(get_optional_current_user),
    ) -> None:
        subject = (
            current_user.id
            if current_user is not None
            else (request.client.host if request.client is not None else "anonymous")
        )
        window_slot = int(time()) // window_seconds
        cache_key = f"rate-limit:{scope}:{subject}:{window_slot}"

        request_count = await redis_client.incr(cache_key)
        if request_count == 1:
            await redis_client.expire(cache_key, window_seconds)

        if request_count > limit:
            retry_after_seconds = await redis_client.ttl(cache_key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit superato. Riprovare piu tardi.",
                headers={"Retry-After": str(max(retry_after_seconds, 1))},
            )

    return dependency
