from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.auth import get_current_user
from app.schemas.user import UserDisplay, UserUpdate
from app.schemas.skill import UserSkillDisplay
from app.services.user import UserService
from app.services.skill import UserSkillService
from app.models.user import User
from app.limiter import limiter

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserDisplay)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """View your own profile."""
    return current_user


@router.get("/{user_id}", response_model=UserDisplay)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    """View any user's public profile."""
    return UserService(db).get_profile(user_id)


@router.patch("/me", response_model=UserDisplay)
@limiter.limit("20/minute")
def update_profile(
    request: Request,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Edit your profile info."""
    return UserService(db).update_profile(current_user, data)


@router.get("/me/skills", response_model=list[UserSkillDisplay])
def my_skills(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all skills you've learned."""
    return UserSkillService(db).list_my_skills(current_user)
