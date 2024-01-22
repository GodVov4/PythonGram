from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from src.entity.models import Role


class UserSchema(BaseModel):
    full_name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=4, max_length=20)


class UserResponse(BaseModel):
    id: int = 1
    full_name: str
    email: EmailStr
    avatar: str | None
    role: Role
    picture_count: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class AnotherUsers(BaseModel):
    full_name: str
    email: EmailStr
    avatar: str
    picture_count: Optional[int]
    created_at: datetime


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
