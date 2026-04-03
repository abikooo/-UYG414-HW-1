from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.user import UserCreate, UserLogin, UserOrm, UserRole
from repositories.user_repository import UserRepository
from core.security import verify_password, create_access_token, create_refresh_token
from core.config import settings
from datetime import timedelta
from jose import jwt, JWTError

class AuthService:
    def __init__(self, session: Session):
        self.repository = UserRepository(session)

    def register(self, user_in: UserCreate) -> UserOrm:
        existing_user = self.repository.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(status_code=400, detail={"status": "error", "error": "Email already registered"})
        return self.repository.create(user_in)

    def login(self, login_in: UserLogin) -> dict:
        user = self.repository.get_by_email(login_in.email)
        if not user or not verify_password(login_in.password, user.hashed_password):
            raise HTTPException(status_code=401, detail={"status": "error", "error": "Invalid email or password"})
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": str(user.id), "role": user.role.value}
        
        access_token = create_access_token(payload, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(payload)

        return {"access_token": access_token, "refresh_token": refresh_token}
        
    def refresh(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id: str = payload.get("sub")
            role: str = payload.get("role")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user = self.repository.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
                
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            new_payload = {"sub": str(user.id), "role": user.role.value}
            access_token = create_access_token(new_payload, expires_delta=access_token_expires)
            return {"access_token": access_token, "refresh_token": token}

        except JWTError:
            raise HTTPException(status_code=401, detail={"status": "error", "error": "Could not validate credentials"})

    def verify(self, user_id: str) -> UserOrm:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail={"status": "error", "error": "User not found"})
        return user
