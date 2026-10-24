from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from app.db import Base


class RequestStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class Clan(Base):
    __tablename__ = "clans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    is_public = Column(Boolean, default=True, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    creator = relationship("User", back_populates="owned_clan", foreign_keys=[creator_id])
    members = relationship("User", back_populates="clan", foreign_keys="User.clan_id")
    join_requests = relationship("JoinRequest", back_populates="clan", cascade="all, delete-orphan")


class JoinRequest(Base):
    __tablename__ = "join_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    clan_id = Column(Integer, ForeignKey("clans.id", ondelete="CASCADE"), nullable=False)
    status = Column(SAEnum(RequestStatus), nullable=False, default=RequestStatus.pending)

    user = relationship("User", back_populates="join_requests")
    clan = relationship("Clan", back_populates="join_requests")
