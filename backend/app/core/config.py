from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Global application settings loaded from .env
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # -------------------------
    # Application
    # -------------------------
    APP_NAME: str = "AI Career Operating System"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # -------------------------
    # Server
    # -------------------------
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # -------------------------
    # Security
    # -------------------------
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # -------------------------
    # Database
    # -------------------------
    DATABASE_URL: str

    # -------------------------
    # Redis
    # -------------------------
    REDIS_URL: str

    # -------------------------
    # CORS
    # -------------------------
    BACKEND_CORS_ORIGINS: str
    
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # -------------------------
    # Integrations & Security
    # -------------------------
    ENCRYPTION_KEY: str

    FRONTEND_URL: str = "http://localhost:5173"

    # Public origin of THIS backend, used to build absolute OAuth redirect URIs.
    # HOST/PORT are bind addresses ("0.0.0.0") and must never be used for that.
    PUBLIC_BASE_URL: str = "http://localhost:8000"

    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_TENANT: str = "common"
    HUGGINGFACE_CLIENT_ID: str = ""
    HUGGINGFACE_CLIENT_SECRET: str = ""

    # -------------------------
    # Integration sync policy
    # -------------------------
    OAUTH_STATE_TTL_SECONDS: int = 600
    SYNC_MIN_INTERVAL_SECONDS: int = 60          # throttle: no hammering providers
    SYNC_MAX_ATTEMPTS: int = 3                   # bounded retries, never infinite
    SYNC_BACKOFF_BASE_SECONDS: float = 2.0
    PROVIDER_HTTP_TIMEOUT_SECONDS: float = 20.0

    # -------------------------
    # Email delivery (password reset / verification)
    # -------------------------
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_USE_SSL: bool = False
    EMAIL_FROM: str = ""
    EMAIL_FROM_NAME: str = "AI Career OS"
    # When SMTP is unconfigured in a dev environment, write the message to this
    # directory instead of pretending it was sent.
    EMAIL_DEV_OUTBOX: str = "var/mail"

    PASSWORD_RESET_TOKEN_TTL_MINUTES: int = 30
    EMAIL_VERIFICATION_TOKEN_TTL_HOURS: int = 48

    @property
    def email_configured(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAIL_FROM)


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    """
    return Settings()


settings = get_settings()
