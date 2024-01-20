from datetime import datetime
from typing import Optional, Dict, Union

from pydantic import BaseModel, Field


class TransformCreate(BaseModel):
    transformation_params: Dict[str, Union[str, int]] = Field(
        default_factory=dict,
        example={"width": 500, "height": 300, "crop": "fill",
                 "effect": "grayscale"
                 }
    )


class TransformUpdate(TransformCreate):
    pass


class TransformResponse(BaseModel):
    id: int
    original_picture_id: int
    url: str
    qr_url: Optional[str]
    # transformation_params: Optional[dict]
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True
