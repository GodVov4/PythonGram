from datetime import datetime

from pydantic import BaseModel


class CommentSchema(BaseModel):
    id: int = 1
    picture_id: int = 1
    text: str


class CommentResponse(CommentSchema):
    user_id: int = 1
    created_at: datetime
    updated_at: datetime
