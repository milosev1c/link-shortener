"""Storage backend factory."""

from link_shortener.config import Settings
from link_shortener.storage.base import URLStorage
from link_shortener.storage.postgres import PostgresStorage
from link_shortener.storage.redis import RedisStorage


def create_storage(settings: Settings) -> URLStorage:
    if settings.storage_backend == "redis":
        return RedisStorage(str(settings.redis_url))
    return PostgresStorage(
        str(settings.postgres_dsn),
        min_size=settings.postgres_pool_min_size,
        max_size=settings.postgres_pool_max_size,
    )
