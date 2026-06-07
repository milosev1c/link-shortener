from unittest.mock import AsyncMock

import link_shortener.api.routes as routes_module
from httpx import ASGITransport, AsyncClient
from link_shortener.main import create_app
from link_shortener.storage.base import StorageError


async def test_health_returns_ok(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_health_storage_failure_returns_503(memory_storage):
    memory_storage.get = AsyncMock(side_effect=StorageError("down"))
    app = create_app(storage=memory_storage)
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}


async def test_app_title(client):
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "link-shortener"


def test_routes_module_importable():
    assert hasattr(routes_module, "router")
