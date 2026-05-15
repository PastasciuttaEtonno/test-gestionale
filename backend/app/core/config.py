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
    login_rate_limit_max_attempts: int = 5
    login_rate_limit_window_minutes: int = 15
    login_rate_limit_lockout_minutes: int = 15
    cors_allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )
    refresh_cookie_name: str = "esseduesoft_refresh_token"
    refresh_cookie_secure: bool = False
    refresh_cookie_samesite: str = "lax"
    refresh_cookie_path: str = "/api/v1/auth"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
