import pytest
from fastapi.testclient import TestClient

from app.main import app

VALID_KEY = "dev-secret-key"


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


class TestHealthEndpoint:
    def test_health_returns_200(self, client: TestClient) -> None:
        r = client.get("/api/v1/health")
        assert r.status_code == 200

    def test_health_schema(self, client: TestClient) -> None:
        data = client.get("/api/v1/health").json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "service" in data


class TestAnalyzeEndpoint:
    def test_valid_request_returns_200(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/analyze",
            json={"text": "FastAPI is an amazing framework for building REST APIs!"},
            headers={"X-API-Key": VALID_KEY},
        )
        assert r.status_code == 200

    def test_response_schema(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/analyze",
            json={"text": "FastAPI is an amazing framework for building REST APIs!"},
            headers={"X-API-Key": VALID_KEY},
        )
        data = r.json()
        assert "sentiment" in data
        assert data["sentiment"] in ("positive", "neutral", "negative")
        assert "sentiment_score" in data
        assert isinstance(data["keywords"], list)
        assert isinstance(data["word_count"], int)
        assert isinstance(data["char_count"], int)
        assert "model_used" in data

    def test_wrong_api_key_returns_403(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/analyze",
            json={"text": "Hello world, this is a test."},
            headers={"X-API-Key": "totally-wrong-key"},
        )
        assert r.status_code == 403

    def test_missing_api_key_returns_403(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/analyze",
            json={"text": "Hello world, this is a test."},
        )
        assert r.status_code == 403

    def test_text_too_short_returns_422(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/analyze",
            json={"text": "Hi"},
            headers={"X-API-Key": VALID_KEY},
        )
        assert r.status_code == 422

    def test_positive_sentiment_detected(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/analyze",
            json={"text": "This is absolutely amazing, wonderful and fantastic work!"},
            headers={"X-API-Key": VALID_KEY},
        )
        assert r.status_code == 200
        assert r.json()["sentiment"] == "positive"

    def test_negative_sentiment_detected(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/analyze",
            json={"text": "This is terrible, awful, horrible and the worst possible outcome."},
            headers={"X-API-Key": VALID_KEY},
        )
        assert r.status_code == 200
        assert r.json()["sentiment"] == "negative"

    def test_keywords_returned(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/analyze",
            json={"text": "Python Python Python is great great great for APIs."},
            headers={"X-API-Key": VALID_KEY},
        )
        data = r.json()
        assert "python" in data["keywords"]

    def test_metrics_endpoint_accessible(self, client: TestClient) -> None:
        r = client.get("/metrics")
        assert r.status_code == 200
        assert "http" in r.text
