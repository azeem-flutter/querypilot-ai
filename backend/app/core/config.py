"""Validated settings from environment / backend/.env (secrets code mein hard-code nahi)."""
from functools import lru_cache
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

FORBIDDEN_DB_ROLES = {"postgres", "service_role", "supabase_admin"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"

    # ---- Database (Day 1): sirf restricted role, kabhi owner / service_role nahi
    database_url: str = Field(..., min_length=10)
    sql_statement_timeout_ms: int = Field(3000, ge=100, le=30000)
    sql_max_rows: int = Field(100, ge=1, le=1000)
    db_pool_min: int = Field(1, ge=1)
    db_pool_max: int = Field(5, ge=1, le=20)

    # ---- LLM (Day 2)
    llm_provider: Literal["groq", "fake"] = "groq"
    llm_model: str = ""
    llm_api_key: SecretStr | None = None          # SecretStr: print/log mein '**********' dikhta hai
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_timeout_seconds: float = Field(30.0, gt=0, le=120)
    llm_max_output_tokens: int = Field(1200, ge=100, le=4000)
    llm_temperature: float = Field(0.0, ge=0.0, le=1.0)
    # json_schema sirf chuninda models par chalta hai; json_object sab par.
    # Local Pydantic validation hamesha hoti hai.
    llm_json_mode: Literal["json_schema", "json_object"] = "json_object"
    # Sirf reasoning models (jaise gpt-oss) ke liye. Khali = parameter bheja hi nahi jata.
    llm_reasoning_effort: Literal["", "low", "medium", "high"] = ""

    @field_validator("database_url")
    @classmethod
    def _must_be_restricted_postgres_url(cls, v: str) -> str:
        parsed = urlparse(v)
        if parsed.scheme not in ("postgresql", "postgres"):
            raise ValueError("DATABASE_URL must start with postgresql://")
        role = (parsed.username or "").split(".")[0]
        if role in FORBIDDEN_DB_ROLES:
            raise ValueError(
                f"DATABASE_URL uses privileged role '{role}'. Use the restricted 'query_readonly' role."
            )
        return v

    @property
    def llm_configured(self) -> bool:
        if self.llm_provider == "fake":
            return True
        return bool(self.llm_api_key and self.llm_api_key.get_secret_value() and self.llm_model)


@lru_cache
def get_settings() -> Settings:
    return Settings()