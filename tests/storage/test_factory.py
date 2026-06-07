from link_shortener.config import Settings
from link_shortener.storage.factory import create_storage
from link_shortener.storage.postgres import PostgresStorage
from link_shortener.storage.redis import RedisStorage


def test_create_redis_storage():
    settings = Settings(storage_backend="redis")
    storage = create_storage(settings)
    assert isinstance(storage, RedisStorage)


def test_create_postgres_storage():
    settings = Settings(storage_backend="postgres")
    storage = create_storage(settings)
    assert isinstance(storage, PostgresStorage)
