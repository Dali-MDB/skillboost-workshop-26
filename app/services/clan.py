from typing import List, Optional
from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.repositories.clan import ClanRepository, JoinRequestRepository
from app.repositories.user import UserRepository
from app.schemas.clan import ClanCreate, ClanUpdate, ClanDisplay, JoinRequestDisplay
from app.services.email import EmailService
from app.models.clan import Clan, RequestStatus
from app.models.user import User


class ClanService:
    def __init__(self, db: Session) -> None:
        self.repo = ClanRepository(db)
        self.jr_repo = JoinRequestRepository(db)
        self.user_repo = UserRepository(db)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _to_display(self, clan: Clan) -> ClanDisplay:
        return ClanDisplay(
            id=clan.id,
            name=clan.name,
            description=clan.description,
            is_public=clan.is_public,
            creator_id=clan.creator_id,
            member_count=len(clan.members),
        )

    def _require_creator(self, clan: Clan, user: User) -> None:
        if clan.creator_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the clan creator can do this")

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def create_clan(self, user: User, data: ClanCreate) -> ClanDisplay:
        if user.clan_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Leave your current clan first")
        if self.repo.get_by_name(data.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Clan name already taken")
        clan = self.repo.create(
            name=data.name,
            description=data.description,
            is_public=data.is_public,
            creator_id=user.id,
        )
        # Creator auto-joins
        user.clan_id = clan.id
        self.user_repo.db.commit()
        return self._to_display(clan)

    def list_clans(self) -> List[ClanDisplay]:
        return [self._to_display(c) for c in self.repo.list_all()]

    def get_clan(self, clan_id: int) -> ClanDisplay:
        clan = self.repo.get_by_id(clan_id)
        if not clan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clan not found")
        return self._to_display(clan)

    def update_clan(self, user: User, clan_id: int, data: ClanUpdate) -> ClanDisplay:
        clan = self.repo.get_by_id(clan_id)
        if not clan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clan not found")
        self._require_creator(clan, user)
        updated = self.repo.update(clan, **data.model_dump(exclude_unset=True))
        return self._to_display(updated)

    def close_clan(self, user: User, clan_id: int) -> None:
        clan = self.repo.get_by_id(clan_id)
        if not clan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clan not found")
        self._require_creator(clan, user)
        # Remove all members from clan
        for member in clan.members:
            member.clan_id = None
        self.repo.delete(clan)

    # ── Membership ────────────────────────────────────────────────────────────

    def join_or_request(self, user: User, clan_id: int, background_tasks: Optional[BackgroundTasks] = None) -> dict:
        clan = self.repo.get_by_id(clan_id)
        if not clan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clan not found")
        if user.clan_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Leave your current clan first")
        existing = self.jr_repo.get_by_user_and_clan(user.id, clan_id)
        if existing and existing.status == RequestStatus.pending:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Join request already pending")

        if clan.is_public:
            user.clan_id = clan_id
            self.user_repo.db.commit()
            return {"message": "Joined clan successfully"}
        else:
            self.jr_repo.create(user_id=user.id, clan_id=clan_id)
            if background_tasks and clan.creator:
                background_tasks.add_task(
                    EmailService.send_join_request_email,
                    clan.creator.email,
                    user.username,
                    clan.name,
                )
            return {"message": "Join request sent, waiting for approval"}

    def leave_clan(self, user: User) -> dict:
        if not user.clan_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not in a clan")
        clan = self.repo.get_by_id(user.clan_id)
        if clan and clan.creator_id == user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Creator cannot leave — close the clan instead",
            )
        user.clan_id = None
        self.user_repo.db.commit()
        return {"message": "Left the clan"}

    # ── Join Request management (creator only) ────────────────────────────────

    def list_requests(self, user: User, clan_id: int) -> List[JoinRequestDisplay]:
        clan = self.repo.get_by_id(clan_id)
        if not clan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clan not found")
        self._require_creator(clan, user)
        reqs = self.jr_repo.list_for_clan(clan_id, status=RequestStatus.pending)
        return [JoinRequestDisplay.model_validate(r) for r in reqs]

    def accept_request(self, user: User, request_id: int) -> JoinRequestDisplay:
        req = self.jr_repo.get(request_id)
        if not req:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
        clan = self.repo.get_by_id(req.clan_id)
        if not clan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clan not found")
        self._require_creator(clan, user)
        if req.status != RequestStatus.pending:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request is not pending")
        # Accept: add member
        applicant = self.user_repo.get_by_id(req.user_id)
        if not applicant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Applicant user not found")
        if applicant.clan_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already belongs to a clan")
        applicant.clan_id = req.clan_id
        self.user_repo.db.commit()
        req = self.jr_repo.update_status(req, RequestStatus.accepted)
        return JoinRequestDisplay.model_validate(req)

    def reject_request(self, user: User, request_id: int) -> JoinRequestDisplay:
        req = self.jr_repo.get(request_id)
        if not req:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
        clan = self.repo.get_by_id(req.clan_id)
        if not clan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clan not found")
        self._require_creator(clan, user)
        if req.status != RequestStatus.pending:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request is not pending")
        req = self.jr_repo.update_status(req, RequestStatus.rejected)
        return JoinRequestDisplay.model_validate(req)
