import pytest
from fakeredis.aioredis import FakeRedis

from link_shortener.storage.redis import LONG_KEY_PREFIX, URL_KEY_PREFIX, RedisStorage


@pytest.fixture
async def redis_storage():
    client = FakeRedis(decode_responses=True)
    storage = RedisStorage("redis://localhost:6379/0")
    storage._client = client
    yield storage
    await storage.disconnect()


@pytest.mark.asyncio
async def test_redis_save_and_get(redis_storage: RedisStorage):
    await redis_storage.save("id1", "https://example.org")

    assert await redis_storage.get("id1") == "https://example.org"


@pytest.mark.asyncio
async def test_redis_find_by_long_url(redis_storage: RedisStorage):
    await redis_storage.save("id1", "https://example.org")

    assert await redis_storage.find_by_long_url("https://example.org") == "id1"


@pytest.mark.asyncio
async def test_redis_writes_dual_keys(redis_storage: RedisStorage):
    await redis_storage.save("id1", "https://example.org")
    client = redis_storage._require_client()

    assert await client.get(f"{URL_KEY_PREFIX}id1") == "https://example.org"
    long_keys = [key async for key in client.scan_iter(f"{LONG_KEY_PREFIX}*")]
    assert len(long_keys) == 1
