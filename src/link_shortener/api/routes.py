"""HTTP route definitions."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from link_shortener.api.deps import get_shortener_service
from link_shortener.api.schemas import ShortenRequest, ShortenResponse
from link_shortener.services.shortener import ShortenerService
from link_shortener.storage.base import StorageError

router = APIRouter()


@router.post("/links/shorten")
async def shorten_url(
    body: ShortenRequest,
    service: ShortenerService = Depends(get_shortener_service),
) -> JSONResponse:
    """Shorten a long URL. Returns 201 for new links, 200 for existing ones."""
    try:
        result = await service.shorten(str(body.long_url))
    except StorageError:
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
