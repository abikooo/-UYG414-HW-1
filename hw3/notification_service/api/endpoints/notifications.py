from fastapi import APIRouter, Depends, Query, Request
from typing import List
from models.notification import NotificationResponse
from services.notification_service import NotificationService
from api.dependencies import get_notification_service

router = APIRouter()

@router.get("", response_model=dict)
def get_notifications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: NotificationService = Depends(get_notification_service)
):
    notifications = service.get_notifications(limit, offset)
    return {
        "status": "success",
        "data": [NotificationResponse.model_validate(n).model_dump() for n in notifications]
    }
