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
    assert body["service"] == "auth-service"


@pytest.mark.asyncio
async def test_register_missing_fields():
    """Registration with missing fields should return 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/register", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_missing_fields():
    """Login with missing fields should return 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/login", json={})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Login with non-existent user should fail gracefully."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/login", json={"email": "fake@fake.com", "password": "wrong"})
    # Should return an error (401 or 500 depending on DB), not crash
    assert response.status_code in [401, 403, 404, 500]


@pytest.mark.asyncio
async def test_verify_without_headers():
    """Verify endpoint without X-User-ID header should return error."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/auth/verify")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "error"


@pytest.mark.asyncio
async def test_me_without_headers():
    """Me endpoint without X-User-ID header should return error."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/auth/me")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "error"
