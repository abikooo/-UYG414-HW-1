from sqlalchemy.orm import Session
from typing import List
from repositories.notification_repository import NotificationRepository
from models.notification import NotificationOrm, NotificationResponse
import logging

logger = logging.getLogger("notification")

class NotificationService:
    def __init__(self, session: Session):
        self.repository = NotificationRepository(session)

    def process_alert(self, payload: dict):
        level = payload.get("level", "UNKNOWN")
        message = payload.get("message", "")
        log_id = payload.get("id", "")
        details = payload.get("metadata", {})
        
        # Simulate sending email/slack
        logger.warning(f"CRITICAL ALERT NOTIFICATION! Log ID: {log_id} | Message: {message} | Details: {details}")

        # Store in DB
        self.repository.create(level=level, message=message, log_id=log_id, details=details)

    def get_notifications(self, limit: int = 50, offset: int = 0) -> List[NotificationOrm]:
        return self.repository.get_all(limit, offset)
