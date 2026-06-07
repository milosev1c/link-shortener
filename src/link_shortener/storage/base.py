"""Storage abstraction for shortened URLs."""

from abc import ABC, abstractmethod


class StorageError(Exception):
    """Raised when a storage backend operation fails."""


class URLStorage(ABC):
    """Async storage backend for short-id to long-url mappings."""

    @abstractmethod
    async def connect(self) -> None:
        """Open connections and prepare the backend."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connections and release resources."""

    @abstractmethod
    async def find_by_long_url(self, long_url: str) -> str | None:
        """Return an existing short id for the long URL, if any."""

    @abstractmethod
    async def get(self, short_id: str) -> str | None:
        """Return the long URL for a short id, if it exists."""

    @abstractmethod
    async def save(self, short_id: str, long_url: str) -> None:
        """Persist a short-id to long-url mapping."""
