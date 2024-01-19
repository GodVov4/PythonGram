from datetime import datetime

from pydantic import BaseModel


class CommentUpdate(BaseModel):
    text: str


class CommentSchema(CommentUpdate):
    picture_id: int


class CommentResponse(CommentSchema):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
