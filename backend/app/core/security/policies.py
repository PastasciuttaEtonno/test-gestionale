"""Policy di autorizzazione."""

from app.domain.security.constants import ADMIN_ROLE


def is_admin(role_code: str) -> bool:
    """Restituisce True quando il ruolo e admin."""
    return role_code == ADMIN_ROLE
