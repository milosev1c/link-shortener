"""FastAPI dependency injection helpers."""

from fastapi import Request

from link_shortener.config import Settings, get_settings
from link_shortener.services.shortener import ShortenerService
from link_shortener.storage.base import URLStorage


def get_app_settings() -> Settings:
    return get_settings()


def get_storage(request: Request) -> URLStorage:
    return request.app.state.storage


def get_shortener_service(request: Request) -> ShortenerService:
    return ShortenerService(request.app.state.storage, request.app.state.settings)
