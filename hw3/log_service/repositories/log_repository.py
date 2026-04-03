from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from models.log_entry import LogEntryOrm, LogLevel, LogCreate
from uuid import UUID

class LogRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, log_in: LogCreate, ai_classification: Optional[str] = None) -> LogEntryOrm:
        new_log = LogEntryOrm(
            service_name=log_in.service_name,
            level=log_in.level,
            message=log_in.message,
            log_metadata=log_in.metadata,
            ai_classification=ai_classification
        )
        self.session.add(new_log)
        self.session.commit()
        self.session.refresh(new_log)
        return new_log

    def get_by_id(self, log_id: UUID) -> Optional[LogEntryOrm]:
        return self.session.query(LogEntryOrm).filter(LogEntryOrm.id == log_id).first()

    def get_list(self, level: Optional[LogLevel], service_name: Optional[str], limit: int, offset: int) -> List[LogEntryOrm]:
        query = self.session.query(LogEntryOrm)
        if level:
            query = query.filter(LogEntryOrm.level == level)
        if service_name:
            query = query.filter(LogEntryOrm.service_name == service_name)
        return query.order_by(LogEntryOrm.timestamp.desc()).offset(offset).limit(limit).all()

    def get_recent_logs(self, limit: int = 50) -> List[LogEntryOrm]:
        return self.session.query(LogEntryOrm).order_by(LogEntryOrm.timestamp.desc()).limit(limit).all()

    def count_total(self) -> int:
        return self.session.query(func.count(LogEntryOrm.id)).scalar()

    def get_counts_by_level(self) -> Dict[str, int]:
        counts = self.session.query(LogEntryOrm.level, func.count(LogEntryOrm.id)).group_by(LogEntryOrm.level).all()
        return {level.name: count for level, count in counts}
