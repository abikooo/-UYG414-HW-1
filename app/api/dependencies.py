from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# rate limiter — 10 requests per minute per IP address
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str | None = Security(_api_key_header),
) -> str:
    """Check the X-API-Key header. Returns the key if valid, raises 403 otherwise."""
    if api_key and api_key == settings.API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid or missing API key.",
    )
