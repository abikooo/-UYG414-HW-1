import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert body["status"] in ["healthy", "degraded"]
    assert body["service"] == "log-service"


@pytest.mark.asyncio
async def test_logs_endpoint_exists():
    """The /api/v1/logs endpoint should exist and be reachable."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/logs")
    # May fail due to missing DB, but should not be 404
    assert response.status_code != 404


@pytest.mark.asyncio
async def test_ingest_log_requires_body():
    """POST to /api/v1/logs without a body should return 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/logs", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_metrics_endpoint_exists():
    """The /api/v1/metrics endpoint should exist."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/metrics")
    assert response.status_code != 404


@pytest.mark.asyncio
async def test_analyze_endpoint_exists():
    """The /api/v1/logs/analyze endpoint should exist."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/logs/analyze")
    assert response.status_code != 404


@pytest.mark.asyncio
async def test_anomalies_endpoint_exists():
    """The /api/v1/logs/anomalies endpoint should exist."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/logs/anomalies")
    assert response.status_code != 404
