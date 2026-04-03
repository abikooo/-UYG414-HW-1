import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import enum
from pydantic import BaseModel, Field, constr
from core.database import Base

class LogLevel(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogEntryOrm(Base):
    __tablename__ = "log_entries"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    service_name = Column(String, nullable=False, index=True)
    level = Column(Enum(LogLevel), nullable=False, index=True)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    log_metadata = Column(JSON, nullable=True)
    ai_classification = Column(String, nullable=True)
    ai_summary = Column(String, nullable=True)

class LogCreate(BaseModel):
    service_name: str
    level: LogLevel
    message: constr(max_length=10000)
    metadata: Optional[Dict[str, Any]] = None

class LogResponse(BaseModel):
    id: uuid.UUID
    service_name: str
    level: LogLevel
    message: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = Field(None, validation_alias="log_metadata", serialization_alias="metadata")
    ai_classification: Optional[str] = None
    ai_summary: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class IncidentSummaryResponse(BaseModel):
    summary: str
    model: str
    latency_ms: int
