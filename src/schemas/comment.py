from datetime import datetime

from pydantic import BaseModel


class CommentSchema(BaseModel):
    picture_id: int
    text: str


class CommentResponse(CommentSchema):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
