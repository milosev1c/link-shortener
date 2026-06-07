"""Redis-backed URL storage."""

import hashlib

import redis.asyncio as redis

from link_shortener.storage.base import StorageError, URLStorage

# Dual-key layout: forward (id -> url) and reverse (url hash -> id) for dedup.
URL_KEY_PREFIX = "url:"
LONG_KEY_PREFIX = "long:"


def _long_url_key(long_url: str) -> str:
    digest = hashlib.sha256(long_url.encode()).hexdigest()
    return f"{LONG_KEY_PREFIX}{digest}"


class RedisStorage(URLStorage):
    """Store mappings in Redis using paired forward and reverse keys."""

    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        self._client: redis.Redis | None = None

    async def connect(self) -> None:
        self._client = redis.Redis.from_url(self._redis_url, decode_responses=True)

    async def disconnect(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _require_client(self) -> redis.Redis:
        if self._client is None:
            raise StorageError("Redis client is not connected")
        return self._client

    async def find_by_long_url(self, long_url: str) -> str | None:
        client = self._require_client()
        try:
            return await client.get(_long_url_key(long_url))
        except redis.RedisError as exc:
            raise StorageError("Redis read failed") from exc

    async def get(self, short_id: str) -> str | None:
        client = self._require_client()
        try:
            return await client.get(f"{URL_KEY_PREFIX}{short_id}")
        except redis.RedisError as exc:
            raise StorageError("Redis read failed") from exc

    async def save(self, short_id: str, long_url: str) -> None:
        client = self._require_client()
        try:
            async with client.pipeline(transaction=True) as pipe:
                pipe.set(f"{URL_KEY_PREFIX}{short_id}", long_url)
                pipe.set(_long_url_key(long_url), short_id)
                await pipe.execute()
        except redis.RedisError as exc:
            raise StorageError("Redis write failed") from exc
