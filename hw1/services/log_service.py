import json
from sqlalchemy.orm import Session
from models.log_entry import LogCreate, LogEntryOrm, LogLevel
from repositories.log_repository import LogRepository
from services.ai_service import AIService
from typing import Optional, List
from uuid import UUID
from core.config import settings
from core.logger import log

class LogService:
    def __init__(self, session: Session):
        self.repository = LogRepository(session)
        self.ai_service = AIService()

    def process_log(self, log_in: LogCreate) -> LogEntryOrm:
        ai_classification = None
        if log_in.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            ai_classification = self.ai_service.classify_log(log_in.message)
            
        new_log = self.repository.create(log_in, ai_classification)
        return new_log

    def get_log(self, log_id: UUID) -> Optional[LogEntryOrm]:
        return self.repository.get_by_id(log_id)

    def list_logs(self, level: Optional[LogLevel], service_name: Optional[str], limit: int, offset: int) -> List[LogEntryOrm]:
        return self.repository.get_list(level, service_name, limit, offset)

    def analyze_recent_logs(self) -> dict:
        recent_logs = self.repository.get_recent_logs(50)
        if not recent_logs:
            return {"summary": "No logs available for analysis.", "model": "none", "latency_ms": 0, "tokens": 0}

        log_strings = []
        for l in recent_logs:
            log_strings.append(f"[{l.timestamp}] {l.level.name} - {l.service_name}: {l.message}")
            
        summary, latency, tokens = self.ai_service.summarize_incident(log_strings)
        return {
            "summary": summary,
            "latency_ms": latency,
            "tokens": tokens
        }

    def get_metrics_data(self) -> dict:
        from core.metrics import metrics_store
        return {
            "total_logs_ingested": self.repository.count_total(),
            "logs_by_level": self.repository.get_counts_by_level(),
            "avg_ai_classification_latency_ms": metrics_store.get_avg_latency(),
            "ai_calls_today": metrics_store.ai_calls_today
        }
