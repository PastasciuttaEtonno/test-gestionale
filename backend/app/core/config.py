"""Impostazioni applicative."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurazione runtime caricata da variabili d'ambiente."""

    app_name: str = "Esseduesoft Core Service"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    database_url: str = Field(default="postgresql+psycopg://app:app@localhost:5432/esseduesoft")
    jwt_secret_key: str = Field(default="change-this-jwt-secret-key-minimum-32-chars")
    field_encryption_key: str = Field(default="5hS0d52CvtQdjq6V2N4xZfJ6S0bFFH4hD4Xf7wYmQx0=")
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "esseduesoft-core-service"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
