from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.dependencies import limiter
from app.api.routes import analyze, health
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.metrics import create_instrumentator
from app.domain.exceptions import SmartTextBaseError


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN001
    configure_logging()
    logger = get_logger(__name__)
    logger.info("startup", service=settings.APP_NAME, version=settings.APP_VERSION)
    yield
    logger.info("shutdown", service=settings.APP_NAME)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "A text analysis API that checks sentiment, extracts keywords, "
            "and returns basic statistics about any given text. "
            "Supports OpenAI integration when an API key is provided."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # slowapi needs this on the app state to work
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    # allow cross-origin requests; restrict allow_origins in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["X-API-Key", "Content-Type"],
    )

    # expose /metrics for Prometheus scraping
    instrumentator = create_instrumentator()
    instrumentator.instrument(app).expose(app, endpoint="/metrics", tags=["Observability"])

    app.include_router(health.router, prefix="/api/v1")
    app.include_router(analyze.router, prefix="/api/v1")

    @app.exception_handler(SmartTextBaseError)
    async def domain_exception_handler(
        request: Request, exc: SmartTextBaseError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.http_status,
            content={"detail": exc.message},
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(
        request: Request, exc: RateLimitExceeded
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded. Maximum 10 requests per minute."},
        )

    return app


app = create_app()
