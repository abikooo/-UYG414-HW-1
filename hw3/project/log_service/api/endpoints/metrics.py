from fastapi import APIRouter, Depends
from services.log_service import LogService
from api.dependencies import get_log_service

router = APIRouter()

@router.get("", response_model=dict)
def get_metrics(service: LogService = Depends(get_log_service)):
    return {"status": "success", "data": service.get_metrics_data()}
