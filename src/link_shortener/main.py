"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from link_shortener.api.routes import router
from link_shortener.config import Settings, get_settings
from link_shortener.storage.base import URLStorage
from link_shortener.storage.factory import create_storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    storage = create_storage(settings)
    await storage.connect()
    app.state.settings = settings
    app.state.storage = storage
    try:
        yield
    finally:
        await storage.disconnect()


def create_app(
    *,
    settings: Settings | None = None,
    storage: URLStorage | None = None,
) -> FastAPI:
    app_settings = settings or get_settings()
    app = FastAPI(title=app_settings.app_name, lifespan=lifespan if storage is None else None)
    app.state.settings = app_settings
    if storage is not None:
        app.state.storage = storage
    app.include_router(router)
    return app


app = create_app()


def run() -> None:
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "link_shortener.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
