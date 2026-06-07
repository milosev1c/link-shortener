"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "link-shortener"
    host: str = "0.0.0.0"
    port: int = 8000

    base_url: AnyHttpUrl = AnyHttpUrl("http://localhost:8000")

    storage_backend: Literal["redis", "postgres"] = "redis"
    redis_url: RedisDsn = RedisDsn("redis://localhost:6379/0")
    postgres_dsn: PostgresDsn = PostgresDsn(
        "postgresql://postgres:postgres@localhost:5432/link_shortener"
    )

    short_id_length: int = 8
    postgres_pool_min_size: int = 2
    postgres_pool_max_size: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()
