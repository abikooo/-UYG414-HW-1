from fastapi import APIRouter, Depends, Query, Path
from typing import List, Optional
from uuid import UUID
import asyncio

from models.log_entry import LogCreate, LogResponse, LogLevel
from services.log_service import LogService
from api.dependencies import get_log_service, require_writer_role
from core.config import settings

router = APIRouter()

@router.post("", response_model=dict, status_code=201, dependencies=[Depends(require_writer_role)])
async def ingest_log(log_in: LogCreate, service: LogService = Depends(get_log_service)):
    new_log = await service.process_log(log_in)
    return {"status": "success", "data": LogResponse.model_validate(new_log).model_dump(by_alias=True)}

@router.get("", response_model=dict)
def list_logs(
    level: Optional[LogLevel] = Query(None),
    service_name: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: LogService = Depends(get_log_service)
):
    logs = service.list_logs(level, service_name, limit, offset)
    return {
        "status": "success",
        "data": [LogResponse.model_validate(l).model_dump(by_alias=True) for l in logs]
    }

@router.get("/{id}", response_model=dict)
def get_log(id: UUID = Path(...), service: LogService = Depends(get_log_service)):
    db_log = service.get_log(id)
    if not db_log:
        return {"status": "error", "error": "Log not found"}
    return {"status": "success", "data": LogResponse.model_validate(db_log).model_dump(by_alias=True)}

@router.post("/analyze", response_model=dict)
def analyze_logs(service: LogService = Depends(get_log_service)):
    result = service.analyze_recent_logs()
    
    return {
        "status": "success",
        "data": {
            "summary": result["summary"],
            "model": settings.CLAUDE_MODEL,
            "latency_ms": result["latency_ms"],
            "tokens": result["tokens"]
        }
    }
