"""PostgreSQL-backed URL storage."""

import asyncpg

from link_shortener.storage.base import StorageError, URLStorage

_SCHEMA = """
CREATE TABLE IF NOT EXISTS shortened_urls (
    short_id   VARCHAR(32) PRIMARY KEY,
    long_url   TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_shortened_urls_long_url ON shortened_urls (long_url);
"""


class PostgresStorage(URLStorage):
    """Store mappings in PostgreSQL via an asyncpg connection pool."""

    def __init__(
        self,
        dsn: str,
        *,
        min_size: int = 2,
        max_size: int = 10,
    ) -> None:
        self._dsn = dsn
        self._min_size = min_size
        self._max_size = max_size
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        try:
            self._pool = await asyncpg.create_pool(
                self._dsn,
                min_size=self._min_size,
                max_size=self._max_size,
            )
            async with self._pool.acquire() as conn:
                await conn.execute(_SCHEMA)
        except asyncpg.PostgresError as exc:
            raise StorageError("PostgreSQL connection failed") from exc

    async def disconnect(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    def _require_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            raise StorageError("PostgreSQL pool is not connected")
        return self._pool

    async def find_by_long_url(self, long_url: str) -> str | None:
        pool = self._require_pool()
        try:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT short_id FROM shortened_urls WHERE long_url = $1",
                    long_url,
                )
        except asyncpg.PostgresError as exc:
            raise StorageError("PostgreSQL read failed") from exc
        return row["short_id"] if row else None

    async def get(self, short_id: str) -> str | None:
        pool = self._require_pool()
        try:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT long_url FROM shortened_urls WHERE short_id = $1",
                    short_id,
                )
        except asyncpg.PostgresError as exc:
            raise StorageError("PostgreSQL read failed") from exc
        return row["long_url"] if row else None

    async def save(self, short_id: str, long_url: str) -> None:
        pool = self._require_pool()
        try:
            async with pool.acquire() as conn:
                # ON CONFLICT handles races; re-fetch ensures caller sees the winner.
                await conn.execute(
                    """
                    INSERT INTO shortened_urls (short_id, long_url)
                    VALUES ($1, $2)
                    ON CONFLICT (long_url) DO NOTHING
                    """,
                    short_id,
                    long_url,
                )
        except asyncpg.PostgresError as exc:
            raise StorageError("PostgreSQL write failed") from exc
