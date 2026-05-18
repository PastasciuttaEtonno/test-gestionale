"""Impostazioni applicative."""

from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_JWT_SECRET_KEY = "change-this-jwt-secret-key-minimum-32-chars"


class Settings(BaseSettings):
    """Configurazione runtime caricata da variabili d'ambiente."""

    app_env: Literal["development", "test", "staging", "production"] = "development"
    app_name: str = "Esseduesoft Core Service"
    app_version: str = "0.1.0"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_json: bool = False
    request_id_header_name: str = "X-Request-ID"
    api_v1_prefix: str = "/api/v1"
    database_url: str = Field(default="postgresql+psycopg://app:app@localhost:5432/esseduesoft")
    jwt_secret_key: str = Field(default=DEFAULT_JWT_SECRET_KEY)
    field_encryption_key: str = Field(default="5hS0d52CvtQdjq6V2N4xZfJ6S0bFFH4hD4Xf7wYmQx0=")
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "esseduesoft-core-service"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    login_rate_limit_max_attempts: int = 5
    login_rate_limit_window_minutes: int = 15
    login_rate_limit_lockout_minutes: int = 15
    login_rate_limit_identifier_max_attempts: int = 10
    login_rate_limit_ip_max_attempts: int = 30
    celery_broker_url: str = "redis://redis_service:6379/0"
    celery_result_backend_url: str = "redis://redis_service:6379/1"
    celery_task_default_queue: str = "default"
    celery_task_track_started: bool = True
    redis_url: str = "redis://redis_service:6379/2"
    dashboard_kpi_cache_ttl_seconds: int = 300
    api_rate_limit_requests_per_minute: int = 100
    cors_allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )
    trusted_proxy_ips: list[str] = Field(default_factory=list)
    auth_allowed_origins: list[str] = Field(default_factory=list)
    auth_enforce_origin_check: bool = False
    refresh_cookie_name: str = "esseduesoft_refresh_token"
    refresh_cookie_secure: bool = False
    refresh_cookie_samesite: str = "lax"
    refresh_cookie_path: str = "/api/v1/auth"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def is_production_like(self) -> bool:
        """Indica se il runtime e orientato a staging o produzione."""
        return self.app_env in {"staging", "production"}

    @property
    def effective_auth_allowed_origins(self) -> list[str]:
        """Restituisce le origin consentite per gli endpoint auth cookie-based."""
        return self.auth_allowed_origins or self.cors_allowed_origins

    @model_validator(mode="after")
    def validate_security_posture(self) -> "Settings":
        """Applica vincoli minimi per evitare configurazioni insicure in produzione."""
        if self.is_production_like and self.jwt_secret_key == DEFAULT_JWT_SECRET_KEY:
            raise ValueError(
                "JWT_SECRET_KEY non puo usare il valore placeholder in staging o produzione."
            )
        if self.is_production_like and not self.refresh_cookie_secure:
            raise ValueError("REFRESH_COOKIE_SECURE deve essere true in staging o produzione.")
        if self.is_production_like and not self.auth_enforce_origin_check:
            raise ValueError("AUTH_ENFORCE_ORIGIN_CHECK deve essere true in staging o produzione.")
        if self.refresh_cookie_name.startswith("__Secure-") and not self.refresh_cookie_secure:
            raise ValueError(
                "Un cookie con prefisso __Secure- richiede REFRESH_COOKIE_SECURE=true."
            )
        if self.refresh_cookie_name.startswith("__Host-") and (
            not self.refresh_cookie_secure or self.refresh_cookie_path != "/"
        ):
            raise ValueError("Un cookie con prefisso __Host- richiede Secure=true e Path=/.")
        if self.refresh_cookie_samesite.lower() == "none" and not self.refresh_cookie_secure:
            raise ValueError("SameSite=None richiede REFRESH_COOKIE_SECURE=true.")
        return self


settings = Settings()
