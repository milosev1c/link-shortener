import pytest

from link_shortener.storage.base import URLStorage
from tests.storage.memory import MemoryURLStorage


@pytest.fixture
async def memory_storage() -> URLStorage:
    storage = MemoryURLStorage()
    await storage.connect()
    yield storage
    await storage.disconnect()


@pytest.fixture(params=["memory"])
def storage(request, memory_storage):
    if request.param == "memory":
        return memory_storage
    raise ValueError(f"Unknown storage fixture: {request.param}")
