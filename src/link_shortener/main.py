"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from link_shortener.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="link-shortener", lifespan=lifespan)
    app.include_router(router)
    return app


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run("link_shortener.main:app", host="0.0.0.0", port=8000, reload=False)
