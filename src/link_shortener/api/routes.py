"""HTTP route definitions."""

import logging
import re

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse

from link_shortener.api.deps import get_shortener_service, get_storage
from link_shortener.api.schemas import ShortenRequest, ShortenResponse
from link_shortener.services.shortener import ShortenerService
from link_shortener.storage.base import StorageError, URLStorage

router = APIRouter()
logger = logging.getLogger(__name__)

_SHORT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
_HEALTHCHECK_PROBE_ID = "__healthcheck__"


@router.get("/health")
async def health(storage: URLStorage = Depends(get_storage)) -> JSONResponse:
    """Liveness/readiness probe; verifies storage is reachable."""
    try:
        await storage.get(_HEALTHCHECK_PROBE_ID)
    except StorageError:
        logger.warning("Storage unavailable during health check")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unavailable"},
        )
    return JSONResponse(content={"status": "ok"})


@router.post("/links/shorten")
async def shorten_url(
    body: ShortenRequest,
    service: ShortenerService = Depends(get_shortener_service),
) -> JSONResponse:
    """Shorten a long URL. Returns 201 for new links, 200 for existing ones."""
    try:
        result = await service.shorten(str(body.long_url))
    except StorageError:
        logger.warning("Storage unavailable during shorten")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Storage unavailable"},
        )

    response = ShortenResponse(short_url=result.short_url)
    status_code = status.HTTP_201_CREATED if result.created else status.HTTP_200_OK
    return JSONResponse(
        content=response.model_dump(mode="json"),
        status_code=status_code,
    )


@router.get("/u/{short_id}")
async def redirect_to_long_url(
    short_id: str,
    storage: URLStorage = Depends(get_storage),
) -> RedirectResponse:
    """Redirect a short id to its original URL with HTTP 307."""
    if not short_id or not _SHORT_ID_PATTERN.fullmatch(short_id):
        raise HTTPException(status_code=404, detail="Short URL not found")

    try:
        long_url = await storage.get(short_id)
    except StorageError:
        logger.warning("Storage unavailable during redirect short_id=%s", short_id)
        raise HTTPException(status_code=503, detail="Storage unavailable") from None

    if long_url is None:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=long_url, status_code=307)
