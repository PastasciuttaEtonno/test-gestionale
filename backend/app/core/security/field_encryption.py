"""Servizio di cifratura per campi sensibili persistiti."""

from cryptography.fernet import Fernet

from app.core.config import settings


class FieldEncryptionService:
    """Gestisce cifratura e decifratura di campi sensibili applicativi."""

    def __init__(self) -> None:
        self.fernet = Fernet(settings.field_encryption_key.encode("utf-8"))

    def encrypt(self, plaintext: str) -> str:
        """Cifra una stringa in chiaro e restituisce il token serializzabile."""
        return self.fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        """Decifra un token serializzato e restituisce la stringa originale."""
        return self.fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
