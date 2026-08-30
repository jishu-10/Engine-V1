from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, Field


def _bool_from_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    app_name: str = Field(default="Similarity Engine V1")
    environment: str = Field(default="local")
    database_url: str = Field(
        default="postgresql+psycopg://similarity:similarity@localhost:5432/similarity"
    )
    create_tables_on_startup: bool = False
    seed_on_startup: bool = False
    log_level: str = "INFO"
    algorithm_version: str = "similarity_v1"
    ontology_version: str = "1.0"
    mapping_version: str = "1.0"
    llm_prompt_version: str = "1.0"
    llm_provider: str = "disabled"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-haiku-4-5"

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        return cls(
            app_name=os.getenv("APP_NAME", "Similarity Engine V1"),
            environment=os.getenv("ENVIRONMENT", "local"),
            database_url=os.getenv(
                "DATABASE_URL",
                "postgresql+psycopg://similarity:similarity@localhost:5432/similarity",
            ),
            create_tables_on_startup=_bool_from_env("CREATE_TABLES_ON_STARTUP", False),
            seed_on_startup=_bool_from_env("SEED_ON_STARTUP", False),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            algorithm_version=os.getenv("ALGORITHM_VERSION", "similarity_v1"),
            ontology_version=os.getenv("ONTOLOGY_VERSION", "1.0"),
            mapping_version=os.getenv("MAPPING_VERSION", "1.0"),
            llm_prompt_version=os.getenv("LLM_PROMPT_VERSION", "1.0"),
            llm_provider=os.getenv("LLM_PROVIDER", "disabled"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or None,
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5"),
        )


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()

