from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.database import Base, engine
from core.logger import setup_logging, log
from core.config import settings

from api.endpoints import logs, health, metrics
from api.middleware import logging_middleware

setup_logging()

# Create DB schema
Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(title=settings.PROJECT_NAME)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"status": "error", "error": exc.errors()}
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "error": str(exc.detail)}
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.add_middleware(BaseHTTPMiddleware, dispatch=logging_middleware)

app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(logs.router, prefix="/api/v1/logs", tags=["logs"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])

@app.on_event("startup")
async def startup_event():
    log.info("application_startup", service=settings.PROJECT_NAME)
