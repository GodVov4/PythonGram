from datetime import datetime

from pydantic import BaseModel, Field


class CommentSchema(BaseModel):
    text: str = Field(min_length=1, max_length=200)


class CommentResponse(CommentSchema):
    id: int
    user_id: int
    picture_id: int
    created_at: datetime
    updated_at: datetime
