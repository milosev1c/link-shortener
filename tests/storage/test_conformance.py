import pytest

from link_shortener.storage.base import URLStorage


@pytest.mark.asyncio
async def test_save_and_get(storage: URLStorage):
    await storage.save("abc123", "https://example.org")

    assert await storage.get("abc123") == "https://example.org"
    assert await storage.get("missing") is None


@pytest.mark.asyncio
async def test_find_by_long_url(storage: URLStorage):
    await storage.save("abc123", "https://example.org")

    assert await storage.find_by_long_url("https://example.org") == "abc123"
    assert await storage.find_by_long_url("https://other.example") is None


@pytest.mark.asyncio
async def test_dedup_on_save(storage: URLStorage):
    await storage.save("first", "https://example.org")
    await storage.save("second", "https://example.org")

    assert await storage.find_by_long_url("https://example.org") == "first"
    assert await storage.get("second") is None
