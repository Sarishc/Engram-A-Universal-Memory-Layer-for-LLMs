"""Configuration management using Pydantic Settings."""

from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Configuration
    app_env: str = Field(default="local", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    port: int = Field(default=8000, alias="PORT")
    debug: bool = Field(default=False, alias="DEBUG")

    # API Configuration
    api_v1_str: str = Field(default="/v1", alias="API_V1_STR")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        alias="CORS_ORIGINS"
    )

    # Provider Configuration
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    google_application_credentials: Optional[str] = Field(
        default=None, alias="GOOGLE_APPLICATION_CREDENTIALS"
    )
    default_embeddings_provider: str = Field(
        default="local", alias="DEFAULT_EMBEDDINGS_PROVIDER"
    )
    default_llm_provider: str = Field(default="openai", alias="DEFAULT_LLM_PROVIDER")

    # Vector Database Configuration
    vector_backend: str = Field(default="chroma", alias="VECTOR_BACKEND")
    chroma_persist_dir: str = Field(default="/data/chroma", alias="CHROMA_PERSIST_DIR")
    pinecone_api_key: Optional[str] = Field(default=None, alias="PINECONE_API_KEY")
    pinecone_index: str = Field(default="engram", alias="PINECONE_INDEX")
    pinecone_environment: str = Field(default="us-west1-gcp", alias="PINECONE_ENVIRONMENT")

    # PostgreSQL Database Configuration
    postgres_host: str = Field(default="postgres", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="engram", alias="POSTGRES_DB")
    postgres_user: str = Field(default="engram", alias="POSTGRES_USER")
    postgres_password: str = Field(default="engram", alias="POSTGRES_PASSWORD")
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")

    # Redis Configuration
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    redis_enabled: bool = Field(default=True, alias="REDIS_ENABLED")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_requests_per_minute: int = Field(
        default=60, alias="RATE_LIMIT_REQUESTS_PER_MINUTE"
    )
    rate_limit_burst_size: int = Field(default=10, alias="RATE_LIMIT_BURST_SIZE")

    # Retrieval Configuration
    rank_alpha: float = Field(default=0.70, alias="RANK_ALPHA")
    rank_beta: float = Field(default=0.20, alias="RANK_BETA")
    rank_gamma: float = Field(default=0.15, alias="RANK_GAMMA")
    rank_delta: float = Field(default=0.05, alias="RANK_DELTA")
    recency_tau_days: float = Field(default=14.0, alias="RECENCY_TAU_DAYS")
    default_top_k: int = Field(default=12, alias="DEFAULT_TOP_K")
    default_max_memories: int = Field(default=6, alias="DEFAULT_MAX_MEMORIES")
    similarity_threshold: float = Field(default=0.92, alias="SIMILARITY_THRESHOLD")
    consolidation_threshold: float = Field(
        default=0.97, alias="CONSOLIDATION_THRESHOLD"
    )

    # Memory Management
    max_text_length: int = Field(default=2048, alias="MAX_TEXT_LENGTH")
    max_memories_per_user: int = Field(
        default=10000, alias="MAX_MEMORIES_PER_USER"
    )
    memory_retention_days: int = Field(default=365, alias="MEMORY_RETENTION_DAYS")
    consolidation_enabled: bool = Field(default=True, alias="CONSOLIDATION_ENABLED")
    forgetting_enabled: bool = Field(default=True, alias="FORGETTING_ENABLED")
    importance_threshold: float = Field(default=0.2, alias="IMPORTANCE_THRESHOLD")
    forgetting_days: int = Field(default=30, alias="FORGETTING_DAYS")

    # Security
    secret_key: str = Field(default="your-secret-key-here-change-in-production", alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(
        default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # Monitoring
    enable_metrics: bool = Field(default=True, alias="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, alias="METRICS_PORT")

    # Multimodal Configuration
    default_image_embeddings: str = Field(default="clip", alias="DEFAULT_IMAGE_EMBEDDINGS")
    whisper_model: str = Field(default="small", alias="WHISPER_MODEL")
    keyframe_sec: int = Field(default=8, alias="KEYFRAME_SEC")
    blob_store_dir: str = Field(default="/data/blobs", alias="BLOB_STORE_DIR")

    # Graph Configuration
    graph_triple_extraction: str = Field(default="heuristic", alias="GRAPH_TRIPLE_EXTRACTION")
    graph_max_radius: int = Field(default=2, alias="GRAPH_MAX_RADIUS")
    spacy_model: str = Field(default="en_core_web_sm", alias="SPACY_MODEL")

    # Chat Configuration
    chat_context_window: int = Field(default=4000, alias="CHAT_CONTEXT_WINDOW")
    chat_max_memories: int = Field(default=10, alias="CHAT_MAX_MEMORIES")
    chat_temperature: float = Field(default=0.7, alias="CHAT_TEMPERATURE")

    # Job Processing Configuration
    rq_dashboard: bool = Field(default=True, alias="RQ_DASHBOARD")
    job_timeout: int = Field(default=300, alias="JOB_TIMEOUT")  # 5 minutes
    job_retry_attempts: int = Field(default=3, alias="JOB_RETRY_ATTEMPTS")

    # Auth Configuration
    api_key_bytes: int = Field(default=32, alias="API_KEY_BYTES")
    api_key_prefix: str = Field(default="ek_", alias="API_KEY_PREFIX")

    # Analytics Configuration
    analytics_retention_days: int = Field(default=90, alias="ANALYTICS_RETENTION_DAYS")
    request_logging_enabled: bool = Field(default=True, alias="REQUEST_LOGGING_ENABLED")

    # Connector Configuration
    google_drive_enabled: bool = Field(default=False, alias="GOOGLE_DRIVE_ENABLED")
    notion_enabled: bool = Field(default=False, alias="NOTION_ENABLED")
    slack_enabled: bool = Field(default=False, alias="SLACK_ENABLED")

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from JSON string or list."""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [v]
        return v

    @validator("database_url", pre=True)
    def build_database_url(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        """Build database URL if not provided."""
        if v:
            return v
        
        return (
            f"postgresql://{values.get('postgres_user', 'engram')}:"
            f"{values.get('postgres_password', 'engram')}@"
            f"{values.get('postgres_host', 'postgres')}:"
            f"{values.get('postgres_port', 5432)}/"
            f"{values.get('postgres_db', 'engram')}"
        )

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env.lower() in ["local", "development", "dev"]

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
