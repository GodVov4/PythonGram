from datetime import datetime
from typing import Optional

from fastapi import File, UploadFile

from pydantic import BaseModel, Field


class PictureSchema(BaseModel):
    file: UploadFile = File(...)
    description: Optional[str] = Field()
    tags: Optional[list[str]] = []


class PictureUpdateSchema(PictureSchema):
    pass


class PictureResponseSchema(BaseModel):
    user_id: int = 1
    url: str
    description: Optional[str] = None
    tags: Optional[list[str]] = []
    created_at: datetime
    # comments: CommentResponseSchema
