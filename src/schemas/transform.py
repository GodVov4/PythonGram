from datetime import datetime
from typing import Optional, Dict, Union

from pydantic import BaseModel, Field


class TransformCreate(BaseModel):
    """
    The TransformCreate model is used to create a new transformed picture.

    :param transformation_params: The transformation parameters to be applied to the image.
    :return: The transformed picture.
    """
    transformation_params: Dict[str, Union[str, int]] = Field(
        default_factory=dict,
        example={"width": 500, "height": 300,
                 "crop": "fill",
                 "effect": "grayscale",
                 "border": "5px_solid_lightblue",
                 "angle": 15,
                 }
    )


class TransformUpdate(TransformCreate):
    """
    The TransformUpdate model is used to update an existing transformed picture.

    :param transformation_params: The transformation parameters to be applied to the image.
    :return: The updated transformed picture.
    """
    pass


class TransformResponse(BaseModel):
    """
    The TransformResponse model is used to return a transformed picture.

    :param id: The ID of the transformed picture.
    :param original_picture_id: The ID of the original picture.
    :param url: The URL of the transformed picture.
    :param qr_url: The URL of the QR code.
    :param user_id: The ID of the user who created the transformed picture.
    :return: The transformed picture.
    """
    id: int
    original_picture_id: int
    url: str
    qr_url: Optional[str]
    # transformation_params: Optional[dict]
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True
