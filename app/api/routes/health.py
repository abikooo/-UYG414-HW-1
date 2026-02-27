from fastapi import APIRouter

from app.core.config import settings
from app.domain.models import HealthResponse

router = APIRouter(tags=["Observability"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns ok when the service is running. No authentication needed.",
)
async def health_check() -> HealthResponse:
    return HealthResponse(version=settings.APP_VERSION, service=settings.APP_NAME)
