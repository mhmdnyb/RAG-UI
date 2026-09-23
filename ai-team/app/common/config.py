"""
Centralized configuration using Pydantic Settings.

Single source of truth for all environment variables.
Usage in any module:
    from common.config import settings
    print(settings.database_url)
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    All configuration is read from environment variables or .env file.
    Field names are case-insensitive and map to env var names.
    """

    # ── Database ──────────────────────────────────────────────
    database_url: str = "postgresql://admin:changeme@localhost:5432/university_db"

    # ── Web Service ───────────────────────────────────────────
    rag_service_port: int = 8000
    rag_service_token: str = ""

    # ── Core Service Callback ─────────────────────────────────
    core_service_url: str = "http://localhost:8080"
    rag_callback_token: str = ""

    # ── LLM ───────────────────────────────────────────────────
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1024

    # ── Embedding ─────────────────────────────────────────────
    embedding_model: str = "text-embedding-3-small"

    # ── Retrieval ─────────────────────────────────────────────
    retrieval_top_k: int = 10
    reranker_top_k: int = 3

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton instance — import this everywhere
settings = Settings()
