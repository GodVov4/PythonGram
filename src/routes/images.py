from fastapi import APIRouter, Depends, status, Path, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import images as repositories_images
from src.schemas.images import PictureSchema, PictureResponseSchema, PictureUpdateSchema
from src.services.auth import auth_service

router = APIRouter(prefix='/images', tags=['images'])


@router.post("/upload_picture", response_model=PictureResponseSchema, status_code=status.HTTP_201_CREATED)
async def upload_picture(
        body: PictureSchema, db: AsyncSession = Depends(get_db),
        user=Depends(auth_service.get_current_user),
):
    picture = await repositories_images.upload_picture(body, db, user)
    if picture is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='SOMETHING WENT WRONG')
    return picture


@router.delete("/{picture_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_picture(
        picture_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        user=Depends(auth_service.get_current_user),
):
    picture = await repositories_images.delete_picture(picture_id, db, user)
    if picture is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='SOMETHING WENT WRONG')
    return picture


@router.put("/{picture_id}", response_model=PictureResponseSchema)
async def update_picture(
        body: PictureUpdateSchema,
        picture_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        user=Depends(auth_service.get_current_user),
):
    picture = await repositories_images.update_picture_description(picture_id, body, db, user)
    if picture is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return picture


@router.get("/{picture_id}", response_model=PictureResponseSchema)
async def get_picture(
        picture_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        user=Depends(auth_service.get_current_user),
):
    picture = await repositories_images.get_picture(picture_id, db, user)
    if picture is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return picture
