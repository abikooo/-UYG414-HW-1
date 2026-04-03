import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from pydantic import BaseModel
from typing import Optional, Dict, Any
from core.database import Base

class NotificationOrm(Base):
    __tablename__ = "notifications"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    level = Column(String, nullable=False, index=True)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    log_id = Column(String, nullable=False)
    details = Column(JSON, nullable=True)

class NotificationResponse(BaseModel):
    id: uuid.UUID
    level: str
    message: str
    timestamp: datetime
    log_id: str
    details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
