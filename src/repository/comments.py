from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Comment, User, Picture
from src.schemas.comment import CommentSchema


async def create_comment(body: CommentSchema, picture_id: int, db: AsyncSession, user: User):
    comment = Comment(**body.model_dump(exclude_unset=True), user_id=user.id, picture_id=picture_id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comments(picture_id: int, offset: int, limit: int, db: AsyncSession):
    stmt = select(Picture).where(Picture.id == picture_id)
    picture = await db.execute(stmt)
    picture = picture.unique().scalar_one_or_none()
    if picture:
        smtp = select(Comment).filter_by(picture_id=picture_id).offset(offset).limit(limit)
        comments = await db.execute(smtp)
        return comments.scalars().all()



async def get_comment(comment_id: int, db: AsyncSession):
    smtp = select(Comment).filter_by(id=comment_id)
    comment = await db.execute(smtp)
    return comment.scalar_one_or_none()


async def update_comment(comment_id: int, body: CommentSchema, db: AsyncSession, user: User):
    stmt = select(Comment).filter_by(id=comment_id, user_id=user.id)
    comment = await db.execute(stmt)
    comment = comment.scalar_one_or_none()
    if comment:
        comment.text = body.text
        await db.commit()
        await db.refresh(comment)
    return comment


async def delete_comment(comment_id: int, db: AsyncSession):
    stmt = select(Comment).filter_by(id=comment_id)
    comment = await db.execute(stmt)
    comment = comment.scalar_one_or_none()
    if comment:
        await db.delete(comment)
        await db.commit()
    return comment
