"""
Configuration.

Values from `.env` live only on this object — they are NOT pushed into
os.environ, so never read configuration with os.environ[...].
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment
    environment: str = "development"  # "development" | "production"

    # Database
    database_url: str = "postgresql://admin:changeme@localhost:5432/university_db"

    # Web Service
    rag_service_port: int = 8000
    rag_service_token: str = ""
    max_question_length: int = 2000

    # Core Service Callback
    core_service_url: str = "http://localhost:8080"
    rag_callback_token: str = ""
    callback_timeout_seconds: float = 10.0
    callback_max_attempts: int = 5

    # False runs jobs inside the API process; development only.
    use_queue: bool = True
    redis_url: str = "redis://localhost:6379/0"
    queue_name: str = "rag_jobs"
    result_ttl_seconds: int = 3600
    pipeline_timeout_seconds: float = 120.0
    retriever_timeout_seconds: float = 45.0
    # Must match the worker's --max-async-tasks (see Makefile).
    max_concurrent_jobs: int = 30
    # Headroom between a job's worst-case duration and the moment Redis
    # hands it to another worker.
    job_idle_margin_seconds: float = 60.0

    # Database pool
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout_seconds: float = 30.0
    db_statement_timeout_ms: int = 30_000

    # ── Default LLM (Global fallback for all LLM calls) ────────
    default_llm_api_key: str = ""
    default_llm_base_url: str | None = None
    default_llm_model: str = "gpt-4o-mini"
    openai_api_key: str = ""  # Standard alias / fallback for default_llm_api_key

    # ── Answer Generation LLM (Overrides default if set) ──────
    llm_api_key: str = ""
    llm_base_url: str | None = None
    llm_model: str = ""
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1024

    # ── Query Router LLM (Overrides default if set) ────────────
    router_api_key: str = ""
    router_base_url: str | None = None
    router_model: str = ""
    router_temperature: float = 0.0

    embedding_model: str = "BAAI/bge-m3"
    embedding_dim: int = 1024
    embedding_device: str = "cpu"
    embedding_batch_size: int = 32
    # Keep near the core count on CPU, low on GPU, or it thrashes.
    embedding_max_concurrency: int = 4

    # Retrieval
    retrieval_top_k: int = 10
    reranker_top_k: int = 3
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    reranker_device: str = "cpu"
    reranker_batch_size: int = 16
    reranker_score_threshold: float = 0.20

    @property
    def effective_default_api_key(self) -> str:
        return self.default_llm_api_key or self.openai_api_key

    @property
    def resolved_llm_api_key(self) -> str:
        return self.llm_api_key or self.effective_default_api_key

    @property
    def resolved_llm_base_url(self) -> str | None:
        return (
            self.llm_base_url
            if self.llm_base_url is not None
            else self.default_llm_base_url
        )

    @property
    def resolved_llm_model(self) -> str:
        return self.llm_model or self.default_llm_model

    @property
    def resolved_router_api_key(self) -> str:
        return self.router_api_key or self.effective_default_api_key

    @property
    def resolved_router_base_url(self) -> str | None:
        return (
            self.router_base_url
            if self.router_base_url is not None
            else self.default_llm_base_url
        )

    @property
    def resolved_router_model(self) -> str:
        return self.router_model or self.default_llm_model

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"production", "prod"}

    @property
    def callback_worst_case_seconds(self) -> float:
        attempts = max(1, self.callback_max_attempts)
        backoff = sum(2**i for i in range(attempts - 1))
        return attempts * self.callback_timeout_seconds + backoff

    @property
    def job_idle_timeout_seconds(self) -> float:
        """Longer than any single task can legitimately run."""
        longest = max(self.pipeline_timeout_seconds, self.callback_worst_case_seconds)
        return longest + self.job_idle_margin_seconds


settings = Settings()


def validate_settings() -> None:
    """Refuse to start in production without the shared tokens."""
    from app.common.exceptions import ConfigurationError

    if not settings.is_production:
        return

    missing = []
    if not settings.rag_service_token:
        missing.append("RAG_SERVICE_TOKEN")
    if not settings.rag_callback_token:
        missing.append("RAG_CALLBACK_TOKEN")
    if missing:
        raise ConfigurationError(
            "Missing required production settings: " + ", ".join(missing)
        )
