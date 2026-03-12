from fastapi import APIRouter, Depends
from api.dependencies import verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])

@router.get("", response_model=dict)
def health_check():
    return {"status": "success", "data": {"message": "Service is healthy"}}
