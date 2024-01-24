
from fastapi import UploadFile, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Picture, User, Role
from src.schemas.images import PictureSchema, PictureUpdateSchema
from src.services.cloudstore import CloudService
from src.repository import tags as repository_tags

async def access_check(user: User, picture_user_id, role):
    print(role)
    print(type(role))
    if user.id == picture_user_id:
        return True
    elif role == Role.admin:
        return True
    else:
        return False


async def upload_picture(file: UploadFile, body: PictureSchema, db: AsyncSession, user: User):
    image = await CloudService.upload_picture(user.id, file)
    prepared_tags = []

    if image:
        image_url, public_id = image
        picture = Picture(url=image_url, description=body.description, cloudinary_public_id=public_id, user_id=user.id)

        if body.tags:
            tags = [tag.strip() for tag in body.tags.split(',')]
            if len(tags) > 5:
                await CloudService.delete_picture(public_id)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Максимальна кількість тегів - 5")
            for tag in tags:
                result = await repository_tags.create_tag(tag, db)
                prepared_tags.append(result)

        for tag_name in prepared_tags:
            picture.tags.append(tag_name)
        db.add(picture)
        await db.commit()
        await db.refresh(picture)

    image_url, _ = image
    stmt = select(Picture).where(Picture.url == image_url)
    picture = await db.execute(stmt)
    picture = picture.unique().scalar_one_or_none()
    return {
        'user_id': picture.user_id,
        'picture_id': picture.id,
        'url': picture.url,
        'description': picture.description,
        'tags': [tag.name for tag in picture.tags],
        'created_at': picture.created_at,
        'comments': picture.comment,
        }


async def delete_picture(picture_id: int, db: AsyncSession, user: User):
    stmt = select(Picture).where(Picture.id == picture_id)
    picture = await db.execute(stmt)
    picture = picture.unique().scalar_one_or_none()
    if picture:
        if not await access_check(user, picture.user_id, user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='Доступ заборонено: відсутні права на редагування'
            )

        await CloudService.delete_picture(picture.cloudinary_public_id)
        await db.delete(picture)
        await db.commit()
        return 'Success'
    return picture


async def update_picture_description(picture_id: int, body: PictureUpdateSchema, db: AsyncSession, user: User):
    stmt = select(Picture).where(Picture.id == picture_id)
    picture = await db.execute(stmt)
    picture = picture.unique().scalar_one_or_none()
    if picture:
        if not await access_check(user, picture.user_id, user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='Доступ заборонено: відсутні права на редагування'
            )

        picture.description = body.description
        await db.commit()
        await db.refresh(picture)
        return {
            'user_id': picture.user_id,
            'picture_id': picture.id,
            'url': picture.url,
            'description': picture.description,
            'tags': [tag.name for tag in picture.tags],
            'created_at': picture.created_at,
            'comments': [comment.text for comment in picture.comment],
        }
    return picture


async def get_picture(picture_id: int, db: AsyncSession, user: User):
    stmt = select(Picture).where(Picture.id == picture_id)
    picture = await db.execute(stmt)
    picture = picture.unique().scalar_one_or_none()
    if picture:
        if not await access_check(user, picture.user_id, user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='Доступ заборонено: відсутні права на редагування'
            )

        result = {
            'user_id': picture.user_id,
            'picture_id': picture.id,
            'url': picture.url,
            'description': picture.description,
            'tags': [tag.name for tag in picture.tags],
            'created_at': picture.created_at,
            'comments': [comment.text for comment in picture.comment],
        }
        return result
    return picture
