import logging

import httpx
from fastapi import APIRouter
from pydantic import BaseModel, HttpUrl

router = APIRouter()
logger = logging.getLogger(__name__)


class URLCheckRequest(BaseModel):
    url: HttpUrl


class URLCheckResponse(BaseModel):
    accessible: bool
    status_code: int | None = None
    error: str | None = None


@router.post("/check-url", response_model=URLCheckResponse)
async def check_url(request: URLCheckRequest) -> URLCheckResponse:
    try:
        timeout = httpx.Timeout(10.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.head(str(request.url))
            return URLCheckResponse(
                accessible=response.status_code < 400,
                status_code=response.status_code
            )
    except httpx.TimeoutException:
        logger.warning(f"Timeout checking URL: {request.url}")
        return URLCheckResponse(accessible=False, error="Timeout")
    except httpx.RequestError as e:
        logger.warning(f"Request error checking URL {request.url}: {e}")
        return URLCheckResponse(accessible=False, error=str(e))
    except Exception as e:
        logger.error(f"Unexpected error checking URL {request.url}: {e}")
        return URLCheckResponse(accessible=False, error="Unknown error")
