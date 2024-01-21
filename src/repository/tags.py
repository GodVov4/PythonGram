from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Tag


async def create_tag(tag: str, db: AsyncSession):
    stmt = select(Tag).where(Tag.name == tag)
    db_tag = await db.execute(stmt)
    db_tag = db_tag.unique().scalar_one_or_none()
    if db_tag:
        return db_tag
    db_tag = Tag(name=tag)
    db.add(db_tag)
    await db.commit()
    await db.refresh(db_tag)
    return db_tag
