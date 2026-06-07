"""In-memory URL storage for tests."""

from link_shortener.storage.base import URLStorage


class MemoryURLStorage(URLStorage):
    def __init__(self) -> None:
        self.by_short_id: dict[str, str] = {}
        self.by_long_url: dict[str, str] = {}

    async def connect(self) -> None:
        return None

    async def disconnect(self) -> None:
        return None

    async def find_by_long_url(self, long_url: str) -> str | None:
        return self.by_long_url.get(long_url)

    async def get(self, short_id: str) -> str | None:
        return self.by_short_id.get(short_id)

    async def save(self, short_id: str, long_url: str) -> None:
        existing = self.by_long_url.get(long_url)
        if existing is not None:
            return
        self.by_short_id[short_id] = long_url
        self.by_long_url[long_url] = short_id
