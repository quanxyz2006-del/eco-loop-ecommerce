"""Environment-backed application settings."""

from functools import lru_cache
import json
from pathlib import Path
from typing import Annotated

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATABASE_URL = f"sqlite:///{(PROJECT_ROOT / 'database' / 'eco_loop.db').as_posix()}"
ENV_FILE = PROJECT_ROOT / "backend" / ".env"


class Settings(BaseSettings):
    """Typed settings loaded from environment variables and ``.env``."""

    app_name: str = "ECO-LOOP API"
    api_prefix: str = "/api/v1"
    # SQLite makes a fresh checkout runnable; set DATABASE_URL to MySQL in production.
    database_url: str = DEFAULT_DATABASE_URL
    secret_key: str = "dev-only-change-this-secret-before-deployment-eco-loop"
    environment: str = "development"
    access_token_expire_minutes: int = 60
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5500", "http://127.0.0.1:5500"]
    admin_email: str | None = None
    admin_password: str | None = None
    superadmin_email: str = "quanxyz2006@gmail.com"
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-3.8-flash"
    mail_server: str | None = None
    mail_port: int = 587
    mail_use_ssl: bool = False
    mail_username: str | None = None
    mail_password: SecretStr | None = None
    mail_from: str | None = None
    mail_from_name: str = "ECO-LOOP Verification"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("api_prefix")
    @classmethod
    def normalize_api_prefix(cls, value: str) -> str:
        """Ensure the API prefix has one leading slash and no trailing slash."""
        return f"/{value.strip('/')}"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        """Accept either a JSON list or a comma-separated environment value."""
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()


settings = get_settings()
