from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.db import get_db
from app.auth import get_current_user
from app.schemas.clan import ClanCreate, ClanUpdate, ClanDisplay, JoinRequestDisplay
from app.services.clan import ClanService
from app.models.user import User
from app.limiter import limiter

router = APIRouter(prefix="/clans", tags=["Clans"])


@router.get("/", response_model=list[ClanDisplay])
def list_clans(db: Session = Depends(get_db)):
    """Browse all clans."""
    return ClanService(db).list_clans()


@router.get("/{clan_id}", response_model=ClanDisplay)
def get_clan(clan_id: int, db: Session = Depends(get_db)):
    """Get a single clan's details."""
    return ClanService(db).get_clan(clan_id)


@router.post("/", response_model=ClanDisplay, status_code=201)
def create_clan(
    data: ClanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new clan (you become the creator and auto-join)."""
    return ClanService(db).create_clan(current_user, data)


@router.patch("/{clan_id}", response_model=ClanDisplay)
@limiter.limit("10/minute")
def update_clan(
    request: Request,
    clan_id: int,
    data: ClanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Modify clan info (creator only)."""
    return ClanService(db).update_clan(current_user, clan_id, data)


@router.delete("/{clan_id}", status_code=204)
def close_clan(
    clan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Permanently close/disband a clan (creator only)."""
    ClanService(db).close_clan(current_user, clan_id)


# ── Membership ────────────────────────────────────────────────────────────────

@router.post("/{clan_id}/join", status_code=200)
@limiter.limit("10/minute")
def join_clan(
    request: Request,
    clan_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Join a public clan directly, or send a join request to a private one."""
    return ClanService(db).join_or_request(current_user, clan_id, background_tasks)


@router.post("/me/leave", status_code=200)
def leave_clan(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Leave your current clan."""
    return ClanService(db).leave_clan(current_user)


# ── Join Request management ───────────────────────────────────────────────────

@router.get("/{clan_id}/requests", response_model=list[JoinRequestDisplay])
def list_requests(
    clan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List pending join requests for your clan (creator only)."""
    return ClanService(db).list_requests(current_user, clan_id)


@router.post("/requests/{request_id}/accept", response_model=JoinRequestDisplay)
def accept_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Accept a join request (creator only)."""
    return ClanService(db).accept_request(current_user, request_id)


@router.post("/requests/{request_id}/reject", response_model=JoinRequestDisplay)
def reject_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject a join request (creator only)."""
    return ClanService(db).reject_request(current_user, request_id)
