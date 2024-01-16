from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Picture, User
from src.schemas.images import PictureSchema, PictureUpdateSchema
from src.services.cloudstore import CloudService


async def upload_picture(body: PictureSchema, db: AsyncSession, user: User):
    image = CloudService.upload_picture(body.file.file, user=user)
    url = image
    description = body.description
    tags = image.tags.split(",") if image.tags else []
    user_id = user.id
    picture = Picture(url=url, description=description, tags=tags, user_id=user_id)
    db.add(picture)
    db.commit()
    db.refresh(picture)


async def delete_picture(picture_id: int, db: AsyncSession, user: User):
    stmt = select(Picture).filter_by(id=picture_id, user=user)
    picture = await db.execute(stmt)
    picture = picture.scalar_one_or_none()
    if picture:
        try:
            CloudService.delete_picture(picture.picture_public_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Помилка видалення зображення: {e}")
        db.delete(picture)
        db.commit()
    return picture

async def update_picture_description(picture_id: int, body: PictureUpdateSchema, db: AsyncSession, user: User):
    stmt = select(Picture).filter_by(id=picture_id, user=user)
    picture = await db.execute(stmt)
    picture = picture.scalar_one_or_none()
    if picture:
        picture.description = body.description
        db.commit()
        db.refresh(picture)
    return picture

async def get_picture(picture_id: int, db: AsyncSession, user: User):
    stmt = select(Picture).filter_by(id=picture_id, user=user)
    picture = await db.execute(stmt)
    return picture.scalar_one_or_none()





