from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from link_shortener.main import create_app
from link_shortener.storage.base import StorageError
from tests.storage.memory import MemoryURLStorage


@pytest.fixture
async def memory_storage():
    storage = MemoryURLStorage()
    await storage.connect()
    yield storage


@pytest.fixture
async def client(memory_storage):
    app = create_app(storage=memory_storage)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_shorten_new_url_returns_201(client):
    response = await client.post(
        "/links/shorten",
        json={"long_url": "https://www.example.org"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["short_url"].startswith("http://localhost:8000/u/")


@pytest.mark.asyncio
async def test_shorten_duplicate_url_returns_200(client):
    payload = {"long_url": "https://www.example.org"}

    first = await client.post("/links/shorten", json=payload)
    second = await client.post("/links/shorten", json=payload)

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["short_url"] == second.json()["short_url"]


@pytest.mark.asyncio
async def test_shorten_invalid_url_returns_422(client):
    response = await client.post("/links/shorten", json={"long_url": "not-a-url"})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_shorten_missing_field_returns_422(client):
    response = await client.post("/links/shorten", json={})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_shorten_storage_failure_returns_503(memory_storage):
    memory_storage.find_by_long_url = AsyncMock(side_effect=StorageError("down"))
    app = create_app(storage=memory_storage)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/links/shorten",
            json={"long_url": "https://www.example.org"},
        )

    assert response.status_code == 503
    assert response.json() == {"detail": "Storage unavailable"}
