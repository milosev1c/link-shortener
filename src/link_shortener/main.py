"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from link_shortener.api.routes import router
from link_shortener.config import Settings, get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(router)
    return app


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run("link_shortener.main:app", host="0.0.0.0", port=8000, reload=False)
