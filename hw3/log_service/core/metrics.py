from typing import List

class MetricsStore:
    def __init__(self):
        self.ai_classification_latencies: List[int] = []
        self.ai_calls_today: int = 0
    
    def record_ai_call(self, latency_ms: int):
        self.ai_calls_today += 1
        self.ai_classification_latencies.append(latency_ms)
        if len(self.ai_classification_latencies) > 1000:
            self.ai_classification_latencies = self.ai_classification_latencies[-1000:]
            
    def get_avg_latency(self) -> float:
        if not self.ai_classification_latencies:
            return 0.0
        return round(sum(self.ai_classification_latencies) / len(self.ai_classification_latencies), 2)

metrics_store = MetricsStore()
