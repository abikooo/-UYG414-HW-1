from sqlalchemy.orm import Session
from typing import List
from models.notification import NotificationOrm, NotificationResponse
from datetime import datetime

class NotificationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, level: str, message: str, log_id: str, details: dict) -> NotificationOrm:
        new_notification = NotificationOrm(
            level=level,
            message=message,
            log_id=log_id,
            details=details,
            timestamp=datetime.utcnow()
        )
        self.session.add(new_notification)
        self.session.commit()
        self.session.refresh(new_notification)
        return new_notification

    def get_all(self, limit: int = 50, offset: int = 0) -> List[NotificationOrm]:
        return self.session.query(NotificationOrm).order_by(NotificationOrm.timestamp.desc()).offset(offset).limit(limit).all()
