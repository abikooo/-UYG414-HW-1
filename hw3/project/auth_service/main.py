from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.database import Base, engine
from api.endpoints import auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"status": "error", "error": exc.errors()})

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"status": "error", "error": str(exc.detail)})

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(auth.router, prefix="/auth", tags=["auth"])
