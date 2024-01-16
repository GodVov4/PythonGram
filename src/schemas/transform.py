from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# class TransformCreate(BaseModel):
#     original_picture_id: int
#     transformation_params: Dict[str, Optional[str]] = Field(
#         default_factory=dict,
#         example={"width": 500, "height": 300, "crop": "fill", "effect": "grayscale"}
#     )

class ResizeParams(BaseModel):
    width: Optional[int] = Field(None, ge=100, le=2000, description="Ширина зображення (від 100 до 2000 пікселів)")
    height: Optional[int] = Field(None, ge=100, le=2000, description="Висота зображення (від 100 до 2000 пікселів)")
    crop: Optional[str] = Field(None, description="Тип обрізки зображення")


class TransformCreate(BaseModel):
    original_picture_id: int = Field(..., description="ID оригінального зображення для трансформації")
    resize_params: Optional[ResizeParams] = Field(
        default=None,
        description="Параметри зміни розміру та обрізки зображення"
    )
    compression_quality: Optional[int] = Field(
        default=75,
        ge=1, le=100,
        description="Рівень компресії та оптимізації якості (від 1 до 100)"
    )
    filter_params: Optional[str] = Field(
        default=None,
        description="Застосування фільтрів, наприклад 'grayscale'"
    )
    rotation_angle: Optional[int] = Field(
        default=0,
        ge=0, le=360,
        description="Кут обертання зображення (від 0 до 360 градусів)"
    )
    mirror: Optional[bool] = Field(
        default=None,
        description="Віддзеркалення зображення (True або False)"
    )

    class Config:
        schema_extra = {
            "example": {
                "original_picture_id": 123,
                "resize_params": {"width": 800, "height": 600, "crop": "fill"},
                "compression_quality": 70,
                "filter_params": "sepia",
                "rotation_angle": 90,
                "mirror": True
            }
        }


class TransformUpdate(TransformCreate):
    pass


class TransformResponse(BaseModel):
    id: int
    original_picture_id: int
    url: str
    qr_url: Optional[str]
    transformation_params: Optional[dict]
    created_at: datetime
    user_id: int

    class Config:
        orm_mode = True

# transformation_params: Dict[str, Optional[str]] = Field(
#         default_factory=dict,
#     )
