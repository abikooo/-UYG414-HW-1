import httpx
from typing import Optional


class APIClient:
    """HTTP client that communicates with the API Gateway."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
        self.refresh_token_str: Optional[str] = None

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # ── Auth ─────────────────────────────────────────────
    def register(self, username: str, email: str, password: str, role: str = "writer") -> dict:
        res = httpx.post(
            f"{self.base_url}/auth/register",
            json={"username": username, "email": email, "password": password, "role": role},
            timeout=10.0,
        )
        return res.json()

    def login(self, email: str, password: str) -> dict:
        res = httpx.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password},
            timeout=10.0,
        )
        data = res.json()
        if data.get("status") == "success":
            self.token = data["data"]["access_token"]
            self.refresh_token_str = data["data"].get("refresh_token")
        return data

    def get_me(self) -> dict:
        res = httpx.get(f"{self.base_url}/auth/me", headers=self._headers(), timeout=10.0)
        return res.json()

    # ── Logs ─────────────────────────────────────────────
    def ingest_log(self, level: str, message: str, service_name: str = "cli", metadata: dict = None) -> dict:
        payload = {
            "level": level,
            "message": message,
            "service_name": service_name,
            "metadata": metadata or {},
        }
        res = httpx.post(
            f"{self.base_url}/api/v1/logs",
            json=payload,
            headers=self._headers(),
            timeout=15.0,
        )
        return res.json()

    def list_logs(self, level: str = None, service_name: str = None, limit: int = 20) -> dict:
        params = {"limit": limit}
        if level:
            params["level"] = level
        if service_name:
            params["service_name"] = service_name
        res = httpx.get(
            f"{self.base_url}/api/v1/logs",
            params=params,
            headers=self._headers(),
            timeout=10.0,
        )
        return res.json()

    def analyze_logs(self) -> dict:
        res = httpx.post(
            f"{self.base_url}/api/v1/logs/analyze",
            headers=self._headers(),
            timeout=30.0,
        )
        return res.json()

    def detect_anomalies(self) -> dict:
        res = httpx.post(
            f"{self.base_url}/api/v1/logs/anomalies",
            headers=self._headers(),
            timeout=30.0,
        )
        return res.json()

    # ── Health ───────────────────────────────────────────
    def health_gateway(self) -> dict:
        try:
            res = httpx.get(f"{self.base_url}/health", timeout=5.0)
            return res.json()
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}

    def health_service(self, path: str) -> dict:
        try:
            res = httpx.get(f"{self.base_url}/{path}", headers=self._headers(), timeout=5.0)
            return res.json()
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}

    # ── Metrics ──────────────────────────────────────────
    def get_metrics(self) -> dict:
        res = httpx.get(
            f"{self.base_url}/api/v1/metrics",
            headers=self._headers(),
            timeout=10.0,
        )
        return res.json()
