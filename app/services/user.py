from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.auth import hash_password, verify_password, create_access_token
from app.models.user import User


class UserService:
    def __init__(self, db: Session) -> None:
        self.repo = UserRepository(db)

    def register(self, data: UserCreate) -> User:
        if self.repo.get_by_username(data.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
        if self.repo.get_by_email(data.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        hashed = hash_password(data.password)
        return self.repo.create(
            username=data.username,
            email=data.email,
            hashed_password=hashed,
            bio=data.bio,
            avatar_url=data.avatar_url,
        )

    def login(self, email: str, password: str) -> str:
        user = self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return create_access_token({"sub": str(user.id)})

    def get_profile(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def update_profile(self, current_user: User, data: UserUpdate) -> User:
        update_data = data.model_dump(exclude_unset=True)
        return self.repo.update(current_user, **update_data)
