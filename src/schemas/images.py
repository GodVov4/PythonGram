from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.schemas.comment import CommentResponse


class PictureSchema(BaseModel):
    description: Optional[str] = Field()
    tags: Optional[str] = None


class PictureUpdateSchema(BaseModel):
    description: Optional[str] = Field()


class PictureResponseSchema(BaseModel):
    user_id: int
    url: str
    description: Optional[str] = None
    tags: Optional[list[str]] = []
    created_at: datetime
    comments: Optional[list[CommentResponse]] = []
