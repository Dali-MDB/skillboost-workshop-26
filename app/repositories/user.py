from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, username: str, email: str, hashed_password: str, bio: Optional[str], avatar_url: Optional[str]) -> User:
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            bio=bio,
            avatar_url=avatar_url,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, **kwargs) -> User:
        for field, value in kwargs.items():
            if value is not None:
                setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
