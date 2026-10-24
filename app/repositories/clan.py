from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.clan import Clan, JoinRequest, RequestStatus


class ClanRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, clan_id: int) -> Optional[Clan]:
        return self.db.query(Clan).filter(Clan.id == clan_id).first()

    def get_by_name(self, name: str) -> Optional[Clan]:
        return self.db.query(Clan).filter(Clan.name == name).first()

    def list_all(self) -> List[Clan]:
        return self.db.query(Clan).all()

    def create(self, name: str, description: Optional[str], is_public: bool, creator_id: int) -> Clan:
        clan = Clan(name=name, description=description, is_public=is_public, creator_id=creator_id)
        self.db.add(clan)
        self.db.commit()
        self.db.refresh(clan)
        return clan

    def update(self, clan: Clan, **kwargs) -> Clan:
        for field, value in kwargs.items():
            if value is not None:
                setattr(clan, field, value)
        self.db.commit()
        self.db.refresh(clan)
        return clan

    def delete(self, clan: Clan) -> None:
        self.db.delete(clan)
        self.db.commit()


class JoinRequestRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, request_id: int) -> Optional[JoinRequest]:
        return self.db.query(JoinRequest).filter(JoinRequest.id == request_id).first()

    def get_by_user_and_clan(self, user_id: int, clan_id: int) -> Optional[JoinRequest]:
        return (
            self.db.query(JoinRequest)
            .filter(JoinRequest.user_id == user_id, JoinRequest.clan_id == clan_id)
            .first()
        )

    def list_for_clan(self, clan_id: int, status: Optional[RequestStatus] = None) -> List[JoinRequest]:
        q = self.db.query(JoinRequest).filter(JoinRequest.clan_id == clan_id)
        if status:
            q = q.filter(JoinRequest.status == status)
        return q.all()

    def create(self, user_id: int, clan_id: int) -> JoinRequest:
        req = JoinRequest(user_id=user_id, clan_id=clan_id, status=RequestStatus.pending)
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req

    def update_status(self, req: JoinRequest, status: RequestStatus) -> JoinRequest:
        req.status = status
        self.db.commit()
        self.db.refresh(req)
        return req

    def delete(self, req: JoinRequest) -> None:
        self.db.delete(req)
        self.db.commit()
