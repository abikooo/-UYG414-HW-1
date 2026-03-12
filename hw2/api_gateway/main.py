import httpx
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import JSONResponse
from core.config import settings
from jose import jwt, JWTError
import logging

app = FastAPI(title="API Gateway")
logger = logging.getLogger("uvicorn.error")

async def forward_request(method: str, url: str, headers: dict, body: bytes):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.request(method=method, url=url, headers=headers, content=body, timeout=10.0)
            return Response(content=res.content, status_code=res.status_code, headers=dict(res.headers))
        except httpx.RequestError as e:
            logger.error(f"Downstream service unreachable: {str(e)}")
            raise HTTPException(status_code=503, detail={"status": "error", "error": f"Downstream service unreachable"})

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway_route(path: str, request: Request):
    if path == "health":
        return {"status": "success", "data": "Gateway is healthy"}

    headers = dict(request.headers)
    headers.pop("host", None)
    
    # Check if bypassing auth
    if path.startswith("auth/login") or path.startswith("auth/register") or path == "health":
        url = f"{settings.AUTH_SERVICE_URL}/{path}"
        if path.startswith("auth/"):
            url = f"{settings.AUTH_SERVICE_URL}/{path}"
        
        body = await request.body()
        return await forward_request(request.method, url, headers, body)

    # All other routes require auth validation
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"status": "error", "error": "Missing or invalid authorization header"})
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")
        if not user_id or not role:
            raise HTTPException(status_code=401, detail={"status": "error", "error": "Invalid token payload"})
            
        headers["X-User-ID"] = str(user_id)
        headers["X-User-Role"] = str(role)
    except JWTError as e:
        raise HTTPException(status_code=401, detail={"status": "error", "error": f"Invalid token: {str(e)}"})

    body = await request.body()
    
    # Route to appropriate service
    if path.startswith("auth/"):
        url = f"{settings.AUTH_SERVICE_URL}/{path}"
    elif path.startswith("api/v1/logs") or path.startswith("api/v1/metrics") or path.startswith("api/v1/health"):
        url = f"{settings.LOG_SERVICE_URL}/{path}"
    else:
        raise HTTPException(status_code=404, detail={"status": "error", "error": "Route not found in API Gateway"})

    return await forward_request(request.method, url, headers, body)
