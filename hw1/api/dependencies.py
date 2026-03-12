from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from core.database import get_db
from core.config import settings
from services.log_service import LogService

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key or api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail={"error": "Invalid or missing API Key", "status": "error"})
    return api_key

def get_log_service(db: Session = Depends(get_db)):
    return LogService(db)
