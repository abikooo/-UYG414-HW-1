import anthropic
import time
from core.config import settings
from core.logger import log
from core.metrics import metrics_store

class AIService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def classify_log(self, message: str) -> str:
        if not settings.ANTHROPIC_API_KEY:
            return "UNKNOWN"
            
        categories = ["DATABASE_ERROR", "NETWORK_ERROR", "AUTH_ERROR", "PERFORMANCE_ISSUE", "BUSINESS_LOGIC_ERROR", "UNKNOWN"]
        prompt = f"Categorize the following error log into exactly one of these categories: {', '.join(categories)}.\nLog: {message}\nOutput only the category name."
        
        start_time = time.time()
        try:
            response = self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=64,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            latency_ms = int((time.time() - start_time) * 1000)
            category = response.content[0].text.strip()
            
            if category not in categories:
                category = "UNKNOWN"
                
            metrics_store.record_ai_call(latency_ms)
            log.info("ai_call", action="classify", model=settings.CLAUDE_MODEL, tokens=response.usage.input_tokens + response.usage.output_tokens, latency_ms=latency_ms)
            return category
        except Exception as e:
            log.error("ai_call_failed", action="classify", error=str(e))
            return "UNKNOWN"

    def summarize_incident(self, logs_payloads: list[str]) -> tuple[str, int, int]:
        if not settings.ANTHROPIC_API_KEY:
            return "AI API key missing.", 0, 0
            
        prompt = "Analyze the following recent logs and provide a plain-English incident summary with a root cause hypothesis.\nLogs:\n"
        prompt += "\n".join(logs_payloads)
        
        start_time = time.time()
        try:
            response = self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=512,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            latency_ms = int((time.time() - start_time) * 1000)
            metrics_store.record_ai_call(latency_ms)
            tokens = response.usage.input_tokens + response.usage.output_tokens
            log.info("ai_call", action="summarize_incident", model=settings.CLAUDE_MODEL, tokens=tokens, latency_ms=latency_ms)
            return response.content[0].text.strip(), latency_ms, tokens
        except Exception as e:
            log.error("ai_call_failed", action="summarize", error=str(e))
            return f"Error connecting to AI: {e}", 0, 0
