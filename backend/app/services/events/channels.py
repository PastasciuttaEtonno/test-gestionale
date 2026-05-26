"""Convenzioni di naming per i canali Redis Pub/Sub."""

from app.schemas.auth.responses import CurrentUserResponse

TENANT_CHANNEL_PREFIX = "tenant"
ADMIN_CHANNEL = "admin:events"
USER_CHANNEL_PREFIX = "user"


def tenant_channel(tenant_id: str) -> str:
    """Restituisce il canale eventi per un tenant specifico."""
    return f"{TENANT_CHANNEL_PREFIX}:{tenant_id}:events"


def user_channel(user_id: str) -> str:
    """Restituisce il canale eventi personale di un utente."""
    return f"{USER_CHANNEL_PREFIX}:{user_id}:events"


def resolve_channel(user: CurrentUserResponse) -> str:
    """Risolve il canale SSE appropriato in base al ruolo dell'utente."""
    if user.role_code == "admin":
        return ADMIN_CHANNEL
    if user.tenant_id:
        return tenant_channel(user.tenant_id)
    return user_channel(user.id)
