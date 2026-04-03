from fastapi import APIRouter

router = APIRouter()

@router.get("", response_model=dict)
def health_check():
    return {"status": "success", "data": {"message": "Service is healthy"}}
