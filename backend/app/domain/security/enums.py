"""Enumerazioni del dominio sicurezza."""

from enum import StrEnum


class RoleCode(StrEnum):
    """Codici ruolo del sistema."""

    ADMIN = "admin"
    TENANT_ADMIN = "tenant_admin"
    USER = "user"


class AuditEventType(StrEnum):
    """Tipologie di evento audit."""

    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    TOKEN_REFRESH = "token_refresh"
    LOGOUT = "logout"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_STATUS_CHANGED = "user_status_changed"
    USER_ROLE_CHANGED = "user_role_changed"
    ACCESS_DENIED = "access_denied"
