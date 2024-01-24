from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, validator, field_validator

from src.schemas.comment import CommentResponse


class PictureSchema(BaseModel):
    description: Optional[str] = Field(max_length=255)
    tags: Optional[str] = Field(default=None, description='Введіть теги через кому. Максимальна кількість тегів - 5')


class PictureUpdateSchema(BaseModel):
    description: Optional[str] = Field(max_length=255)


class PictureResponseSchema(BaseModel):
    user_id: int
    picture_id: int
    url: str
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    created_at: datetime
    comments: Optional[list[str]] = []
