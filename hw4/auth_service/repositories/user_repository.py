from sqlalchemy.orm import Session
from typing import Optional
from models.user import UserOrm, UserCreate
from core.security import get_password_hash

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> Optional[UserOrm]:
        return self.session.query(UserOrm).filter(UserOrm.email == email).first()

    def get_by_id(self, user_id: str) -> Optional[UserOrm]:
        return self.session.query(UserOrm).filter(UserOrm.id == user_id).first()

    def create(self, user_in: UserCreate) -> UserOrm:
        new_user = UserOrm(
            name=user_in.name,
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            role=user_in.role
        )
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        return new_user
