from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserDisplay(BaseModel):
    id: int
    username: str
    email: str
    bio: Optional[str]
    avatar_url: Optional[str]
    clan_id: Optional[int]

    model_config = {"from_attributes": True}


class TokenDisplay(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
