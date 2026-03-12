from fastapi import Depends, HTTPException, Security, Request
from sqlalchemy.orm import Session
from core.database import get_db
from core.config import settings
from services.log_service import LogService

def get_log_service(db: Session = Depends(get_db)):
    return LogService(db)

def require_writer_role(request: Request):
    role = request.headers.get("X-User-Role")
    if role == "VIEWER":
        raise HTTPException(status_code=403, detail={"status": "error", "error": "VIEWER role cannot modify logs"})
    if not role:
        raise HTTPException(status_code=401, detail={"status": "error", "error": "Missing role header"})
    return role
