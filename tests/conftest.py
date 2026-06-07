import pytest
from httpx import ASGITransport, AsyncClient

from link_shortener.main import create_app
from tests.storage.memory import MemoryURLStorage


@pytest.fixture
async def memory_storage():
    storage = MemoryURLStorage()
    await storage.connect()
    yield storage


@pytest.fixture
def app(memory_storage):
    return create_app(storage=memory_storage)


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
