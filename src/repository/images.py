from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Picture, User, Tag
from src.schemas.images import PictureSchema, PictureUpdateSchema
from src.services.cloudstore import CloudService
from src.repository import tags as repository_tags


async def upload_picture(file: UploadFile, body: PictureSchema, db: AsyncSession, user: User):
    image = await CloudService.upload_picture(user.id, file)
    prepared_tags = []
    if body.tags:
        for tag in body.tags:
            result = await repository_tags.create_tag(tag, db)
            prepared_tags.append(result)
    if image:
        image_url, public_id = image
        # tags = prepared_tags.split(",") if prepared_tags else []
        # user_id = user.id

        picture = Picture(url=image_url, cloudinary_public_id=public_id,
                          description=body.description, user_id=user.id)
        db.add(picture)
        print(prepared_tags)
        for tag in prepared_tags:
            picture.tags = Tag(id=tag.id)
        await db.commit()
        await db.refresh(picture)
        return picture


async def delete_picture(picture_id: int, db: AsyncSession, user: User):
    stmt = select(Picture).filter_by(id=picture_id, user=user.id)
    picture = await db.execute(stmt)
    picture = picture.scalar_one_or_none()
    if picture:
        await CloudService.delete_picture(picture.cloudinary_public_id)
        await db.delete(picture)
        await db.commit()
    return picture


async def update_picture_description(picture_id: int, body: PictureUpdateSchema, db: AsyncSession, user: User):
    stmt = select(Picture).filter_by(id=picture_id, user=user.id)
    picture = await db.execute(stmt)
    picture = picture.scalar_one_or_none()
    if picture:
        picture.description = body.description
        await db.commit()
        await db.refresh(picture)
    return picture


async def get_picture(picture_id: int, db: AsyncSession, user: User):
    stmt = select(Picture).filter_by(id=picture_id, user=user.id)
    picture = await db.execute(stmt)
    return picture.scalar_one_or_none()
