from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db import get_db
from app.auth import get_current_user
from app.schemas.skill import (
    SkillCreate, SkillUpdate, SkillDisplay,
    UserSkillDisplay,
)
from app.services.skill import SkillService, UserSkillService
from app.models.user import User
from app.limiter import limiter

router = APIRouter(prefix="/skills", tags=["Skills"])


# ── Skill catalog (admin-ish, anyone authenticated can add for now) ───────────

@router.get("/", response_model=list[SkillDisplay])
def list_skills(db: Session = Depends(get_db)):
    """Browse all available skills."""
    return SkillService(db).list_skills()


@router.post("/", response_model=SkillDisplay, status_code=201)
def create_skill(data: SkillCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Add a new skill to the catalog."""
    return SkillService(db).create_skill(data)


@router.patch("/{skill_id}", response_model=SkillDisplay)
@limiter.limit("10/minute")
def update_skill(request: Request, skill_id: int, data: SkillUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Update skill metadata."""
    return SkillService(db).update_skill(skill_id, data)


@router.delete("/{skill_id}", status_code=204)
def delete_skill(skill_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Remove a skill from the catalog."""
    SkillService(db).delete_skill(skill_id)


# ── User ↔ Skill (learn / level-up / unlearn) ─────────────────────────────────

@router.post("/learn", response_model=UserSkillDisplay, status_code=201)
def learn_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Learn a new skill (defaults to level 1). Pass skill_id as a query parameter."""
    return UserSkillService(db).learn(current_user, skill_id)


@router.post("/{skill_id}/level-up", response_model=UserSkillDisplay)
@limiter.limit("20/minute")
def level_up_skill(
    request: Request,
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Level up a learned skill by 1 level."""
    return UserSkillService(db).level_up(current_user, skill_id)


@router.delete("/my/{skill_id}", status_code=204)
def unlearn_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Unlearn (remove) a skill from your profile."""
    UserSkillService(db).unlearn(current_user, skill_id)
