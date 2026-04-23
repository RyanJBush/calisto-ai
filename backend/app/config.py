from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Calisto AI"
    environment: str = "development"
    database_url: str = "sqlite:///./calisto.db"
    jwt_secret: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60
    rate_limit_per_minute: int = 300
    cors_origins: List[str] = ["http://localhost:5173"]
    llm_provider: str = "heuristic"
    llm_model: str = "calisto-grounded-v1"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
