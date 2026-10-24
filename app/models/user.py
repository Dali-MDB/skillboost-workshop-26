from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    bio = Column(String(300), nullable=True)
    avatar_url = Column(String(255), nullable=True)

    # clan membership
    clan_id = Column(Integer, ForeignKey("clans.id"), nullable=True)
    clan = relationship("Clan", back_populates="members", foreign_keys=[clan_id])

    # skills (through association)
    user_skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")

    # clan creation
    owned_clan = relationship("Clan", back_populates="creator", foreign_keys="Clan.creator_id", uselist=False)

    # join requests
    join_requests = relationship("JoinRequest", back_populates="user", cascade="all, delete-orphan")
