from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = (
        "Autonomous AI Research & Decision Intelligence Platform"
    )
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = (
        "postgresql+psycopg://research:research@localhost:5432/research"
    )

    API_V1_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"

    MAX_TASKS_PER_RUN: int = 20
    MAX_STEPS_PER_RUN: int = 50
    MAX_TOOL_CALLS_PER_RUN: int = 30
    MAX_RUNTIME_SECONDS: int = 600
    MAX_RETRIES_PER_TASK: int = 2

    GEMINI_API_KEY: str = ""
    MODEL_NAME: str = "gemini-3.8-flash"


@lru_cache
def get_settings() -> Settings:
    return Settings()