"""Validated settings from environment / backend/.env (secrets code mein hard-code nahi)."""
from functools import lru_cache
from urllib.parse import urlparse

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

FORBIDDEN_DB_ROLES = {"postgres", "service_role", "supabase_admin"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"

    # Sirf restricted role (query_readonly). Kabhi owner ya service_role nahi.
    database_url: str = Field(..., min_length=10)

    sql_statement_timeout_ms: int = Field(3000, ge=100, le=30000)
    sql_max_rows: int = Field(100, ge=1, le=1000)
    db_pool_min: int = Field(1, ge=1)
    db_pool_max: int = Field(5, ge=1, le=20)

    @field_validator("database_url")
    @classmethod
    def _must_be_restricted_postgres_url(cls, v: str) -> str:
        parsed = urlparse(v)
        if parsed.scheme not in ("postgresql", "postgres"):
            raise ValueError("DATABASE_URL must start with postgresql://")
        # Supabase pooler username: "<role>.<project-ref>"
        role = (parsed.username or "").split(".")[0]
        if role in FORBIDDEN_DB_ROLES:
            raise ValueError(
                f"DATABASE_URL uses privileged role '{role}'. Use the restricted 'query_readonly' role."
            )
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()  # DATABASE_URL na ho to saaf ValidationError