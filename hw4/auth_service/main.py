from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from core.database import Base, engine
from api.endpoints import auth
from telemetry import setup_telemetry
import sqlalchemy
from logger_setup import setup_app_logging

app = FastAPI(title="Auth Service")
logger = setup_app_logging("auth-service")
setup_telemetry(app, "auth-service")

@app.on_event("startup")
async def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass # In CI/test, database might be missing

@app.get("/health")
async def health_check():
    db_status = "unhealthy"
    try:
        with engine.connect() as connection:
            connection.execute(sqlalchemy.text("SELECT 1"))
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "auth-service",
        "database": db_status
    }

app.include_router(auth.router, prefix="/auth", tags=["auth"])
