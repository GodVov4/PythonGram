from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Comment, User
from src.schemas.comment import CommentSchema, CommentUpdate


async def create_comment(body: CommentSchema, db: AsyncSession, user: User):
    comment = Comment(**body.model_dump(exclude_unset=True), user_id=user.id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comments(picture_id: int, skip: int, limit: int, db: AsyncSession):
    smtp = select(Comment).filter_by(picture_id=picture_id).offset(skip).limit(limit)
    comments = await db.execute(smtp)
    return comments.scalars().all()


async def get_comment(comment_id: int, db: AsyncSession, user: User):
    smtp = select(Comment).filter_by(id=comment_id, user_id=user.id)
    comment = await db.execute(smtp)
    return comment.scalar_one_or_none()


async def update_comment(comment_id: int, body: CommentUpdate, db: AsyncSession, user: User):
    stmt = select(Comment).filter_by(id=comment_id, user_id=user.id)
    comment = await db.execute(stmt)
    comment = comment.scalar_one_or_none()
    if comment:
        comment.text = body.text
        await db.commit()
        await db.refresh(comment)
    return comment


async def delete_comment(comment_id: int, db: AsyncSession, user: User):
    stmt = select(Comment).filter_by(id=comment_id, user_id=user.id)
    comment = await db.execute(stmt)
    comment = comment.scalar_one_or_none()
    if comment:
        await db.delete(comment)
        await db.commit()
    return comment
