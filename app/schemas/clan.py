from pydantic import BaseModel
from typing import Optional
from app.models.clan import RequestStatus


class ClanCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = True


class ClanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class ClanDisplay(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_public: bool
    creator_id: int
    member_count: int = 0

    model_config = {"from_attributes": True}


# ── Join Request ──────────────────────────────────────────────────────────────

class JoinRequestDisplay(BaseModel):
    id: int
    user_id: int
    clan_id: int
    status: RequestStatus

    model_config = {"from_attributes": True}
