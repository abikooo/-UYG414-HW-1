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
    assert body["service"] == "api-gateway"


@pytest.mark.asyncio
async def test_unauthenticated_request_rejected():
    """Requests without a Bearer token to protected routes should get 401."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/logs")
    assert response.status_code == 401
    body = response.json()
    assert body["detail"]["status"] == "error"


@pytest.mark.asyncio
async def test_invalid_token_rejected():
    """A malformed JWT should be rejected with 401."""
    headers = {"Authorization": "Bearer this.is.not.a.valid.jwt"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/logs", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_missing_bearer_prefix_rejected():
    """Authorization header without 'Bearer ' prefix should be rejected."""
    headers = {"Authorization": "Token some-random-token"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/logs", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_unknown_route_returns_404():
    """Routes not matching any service should return 404."""
    from jose import jwt
    token = jwt.encode({"sub": "test-user", "role": "admin"}, "change-this-in-production-long-secret", algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/unknown/path", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_auth_login_route_no_auth_required():
    """Auth login route should be forwarded without needing a token (even if downstream fails)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/login", json={"email": "test@test.com", "password": "pass"})
    # Will be 503 because downstream is not running, but NOT 401
    assert response.status_code != 401


@pytest.mark.asyncio
async def test_auth_register_route_no_auth_required():
    """Auth register route should be forwarded without a token."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/auth/register", json={"username": "u", "email": "e@e.com", "password": "p"})
    assert response.status_code != 401
