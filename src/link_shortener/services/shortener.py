"""URL shortening business logic."""

import secrets
from dataclasses import dataclass

from link_shortener.config import Settings
from link_shortener.storage.base import StorageError, URLStorage


@dataclass(frozen=True, slots=True)
class ShortenResult:
    short_url: str
    created: bool


class ShortenerService:
    """Creates and reuses short URLs backed by pluggable storage."""

    def __init__(self, storage: URLStorage, settings: Settings) -> None:
        self._storage = storage
        self._settings = settings

    async def shorten(self, long_url: str) -> ShortenResult:
        normalized = long_url.strip()

        try:
            existing_id = await self._storage.find_by_long_url(normalized)
        except StorageError as exc:
            raise StorageError("Storage unavailable") from exc

        if existing_id is not None:
            return ShortenResult(
                short_url=self._build_short_url(existing_id),
                created=False,
            )

        short_id = await self._generate_unique_id()
        try:
            await self._storage.save(short_id, normalized)
        except StorageError as exc:
            raise StorageError("Storage unavailable") from exc

        existing_id = await self._storage.find_by_long_url(normalized)
        if existing_id is None:
            raise StorageError("Storage unavailable")

        return ShortenResult(
            short_url=self._build_short_url(existing_id),
            created=existing_id == short_id,
        )

    def _build_short_url(self, short_id: str) -> str:
        base = str(self._settings.base_url).rstrip("/")
        return f"{base}/u/{short_id}"

    async def _generate_unique_id(self) -> str:
        for _ in range(10):
            short_id = secrets.token_urlsafe(self._settings.short_id_length)[: self._settings.short_id_length]
            if await self._storage.get(short_id) is None:
                return short_id
        raise StorageError("Storage unavailable")
