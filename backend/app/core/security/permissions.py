"""Utility legate ai permessi."""


def has_permission(assigned_permissions: set[str], required_permission: str) -> bool:
    """Verifica se il permesso richiesto e assegnato."""
    return required_permission in assigned_permissions
