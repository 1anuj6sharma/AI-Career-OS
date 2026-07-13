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


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    """
    return Settings()


settings = get_settings()
