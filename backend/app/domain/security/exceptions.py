"""Eccezioni del dominio sicurezza."""


class SecurityError(Exception):
    """Eccezione base del dominio sicurezza."""


class InvalidCredentialsError(SecurityError):
    """Sollevata quando le credenziali non sono valide."""


class InvalidTokenError(SecurityError):
    """Sollevata quando un token e non valido o scaduto."""


class InactiveUserError(SecurityError):
    """Sollevata quando l'utente non e attivo."""
