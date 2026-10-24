from pydantic import BaseModel
from typing import Optional


class SkillCreate(BaseModel):
    name: str
    category: str
    description: Optional[str] = None


class SkillUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None


class SkillDisplay(BaseModel):
    id: int
    name: str
    category: str
    description: Optional[str]

    model_config = {"from_attributes": True}


# ── UserSkill (learn / upgrade / unlearn) ─────────────────────────────────────

class UserSkillCreate(BaseModel):
    skill_id: int
    level: int = 1


class UserSkillUpdate(BaseModel):
    level: int


class UserSkillDisplay(BaseModel):
    id: int
    skill_id: int
    skill_name: str
    level: int

    model_config = {"from_attributes": True}
