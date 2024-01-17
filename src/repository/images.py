from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Picture, User
from src.schemas.images import PictureSchema, PictureUpdateSchema
from src.services.cloudstore import CloudService


async def upload_picture(body: PictureSchema, db: AsyncSession, user: User):
    image = CloudService.upload_picture(body.file.file, user=user)  # TODO: (user_id, file) & never awaited
    url = image  # TODO: what is this?
    description = body.description  # TODO: remove this
    tags = image.tags.split(",") if image.tags else []
    user_id = user.id
    picture = Picture(url=url, description=description, tags=tags, user_id=user_id)
    db.add(picture)
    db.commit()  # TODO: never awaited
    db.refresh(picture)  # TODO: never awaited


async def delete_picture(picture_id: int, db: AsyncSession, user: User):
    stmt = select(Picture).filter_by(id=picture_id, user=user)
    picture = await db.execute(stmt)
    picture = picture.scalar_one_or_none()
    if picture:
        try:
            CloudService.delete_picture(picture.picture_public_id)  # TODO: never awaited
        except Exception as e:  # TODO: never excepted, delete_picture do not return errors
            raise HTTPException(status_code=500, detail=f"Помилка видалення зображення: {e}")
        db.delete(picture)  # TODO: never awaited
        db.commit()  # TODO: never awaited
    return picture


async def update_picture_description(picture_id: int, body: PictureUpdateSchema, db: AsyncSession, user: User):
    stmt = select(Picture).filter_by(id=picture_id, user=user)
    picture = await db.execute(stmt)
    picture = picture.scalar_one_or_none()
    if picture:
        picture.description = body.description
        db.commit()  # TODO: never awaited
        db.refresh(picture)  # TODO: never awaited
    return picture


async def get_picture(picture_id: int, db: AsyncSession, user: User):
    stmt = select(Picture).filter_by(id=picture_id, user=user)
    picture = await db.execute(stmt)
    return picture.scalar_one_or_none()
