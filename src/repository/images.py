from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cloudinary.uploader import upload
from cloudinary.models import CloudinaryField

from entity.models_test import Picture, User
from src.schemas.images import PictureSchema, PictureResponseSchema


async def upload_picture(body: PictureSchema, db: AsyncSession, user: User):
    image = upload(body.file.file)
    url = image.get("secure_url")
    description = image.get("description")
    tags = image.tags.split(",") if image.tags else []
    user_id = user
    picture = Picture(url=url, description=description, tags=tags, user_id=user_id)
    db.add(picture)
    db.commit()
    db.refresh(picture)

async def delete_picture(picture_id: int, db: AsyncSession, user: User):
    stmt = select(Picture).filter_by(id=picture_id, user=user)
    picture = await db.execute(stmt)
    picture = picture.scalar_one_or_none()
    if picture:
        db.delete(picture)
        db.commit()
    return picture

async def update_picture_description(picture_id: int, body: PictureSchema, db: AsyncSession, user: User):
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





