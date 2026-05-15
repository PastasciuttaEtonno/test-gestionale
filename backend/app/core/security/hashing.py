"""Utility per hashing e verifica password."""

from pwdlib import PasswordHash


class PasswordHasher:
    """Servizio per hashing e verifica password."""

    def __init__(self) -> None:
        self._password_hash = PasswordHash.recommended()

    def hash_password(self, password: str) -> str:
        """Calcola l'hash di una password in chiaro."""
        return self._password_hash.hash(password)

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        """Verifica una password in chiaro contro un hash salvato."""
        return self._password_hash.verify(plain_password, password_hash)
