from unittest.mock import AsyncMock, MagicMock

import pytest

from link_shortener.storage.postgres import PostgresStorage


@pytest.fixture
def postgres_storage():
    pool = MagicMock()
    conn = AsyncMock()
    pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
    pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)

    storage = PostgresStorage("postgresql://postgres:postgres@localhost/link_shortener")
    storage._pool = pool
    return storage, conn


@pytest.mark.asyncio
async def test_postgres_find_by_long_url(postgres_storage):
    storage, conn = postgres_storage
    conn.fetchrow.return_value = {"short_id": "abc123"}

    result = await storage.find_by_long_url("https://example.org")

    assert result == "abc123"
    conn.fetchrow.assert_awaited_once_with(
        "SELECT short_id FROM shortened_urls WHERE long_url = $1",
        "https://example.org",
    )


@pytest.mark.asyncio
async def test_postgres_get(postgres_storage):
    storage, conn = postgres_storage
    conn.fetchrow.return_value = {"long_url": "https://example.org"}

    result = await storage.get("abc123")

    assert result == "https://example.org"
    conn.fetchrow.assert_awaited_once_with(
        "SELECT long_url FROM shortened_urls WHERE short_id = $1",
        "abc123",
    )


@pytest.mark.asyncio
async def test_postgres_save_uses_on_conflict(postgres_storage):
    storage, conn = postgres_storage

    await storage.save("abc123", "https://example.org")

    conn.execute.assert_awaited_once()
    sql = conn.execute.await_args.args[0]
    assert "ON CONFLICT (long_url) DO NOTHING" in sql
    assert conn.execute.await_args.args[1:] == ("abc123", "https://example.org")
