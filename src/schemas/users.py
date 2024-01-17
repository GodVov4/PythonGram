from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from src.entity.models import Role


class UserSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50)  # TODO: maybe full_name?
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)


class UserResponse(BaseModel):
    id: int = 1
    full_name: str
    email: EmailStr
    avatar: str
    role: Role
    picture_count: int  # TODO: 38 another name
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: str
    email: EmailStr
    avatar: str
    password: str


class AnotherUsers(BaseModel):
    full_name: str
    email: EmailStr
    avatar: str
    photo_count: int  # TODO: 20 another name
    created_at: datetime


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
