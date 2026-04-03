from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from models.user import UserCreate, UserLogin, UserResponse, TokenResponse, RefreshToken
from services.auth_service import AuthService
from api.dependencies import get_auth_service

router = APIRouter()

@router.post("/register", response_model=dict, status_code=201)
def register(user_in: UserCreate, service: AuthService = Depends(get_auth_service)):
    new_user = service.register(user_in)
    return {"status": "success", "data": UserResponse.model_validate(new_user).model_dump()}

@router.post("/login", response_model=dict)
def login(login_in: UserLogin, service: AuthService = Depends(get_auth_service)):
    tokens = service.login(login_in)
    return {"status": "success", "data": tokens}

@router.post("/refresh", response_model=dict)
def refresh(token_in: RefreshToken, service: AuthService = Depends(get_auth_service)):
    tokens = service.refresh(token_in.refresh_token)
    return {"status": "success", "data": tokens}

@router.get("/verify", response_model=dict)
def verify(request: Request, service: AuthService = Depends(get_auth_service)):
    # Gateway validated tokens and sent headers
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        return {"status": "error", "error": "Missing user ID headers"}
    user = service.verify(user_id)
    return {"status": "success", "data": UserResponse.model_validate(user).model_dump()}

@router.get("/me", response_model=dict)
def get_me(request: Request, service: AuthService = Depends(get_auth_service)):
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        return {"status": "error", "error": "Missing credentials"}
    user = service.verify(user_id)
    return {"status": "success", "data": UserResponse.model_validate(user).model_dump()}
