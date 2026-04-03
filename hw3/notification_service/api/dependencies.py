from fastapi import Depends
from sqlalchemy.orm import Session
from core.database import get_db
from services.notification_service import NotificationService

def get_notification_service(db: Session = Depends(get_db)):
    return NotificationService(db)
