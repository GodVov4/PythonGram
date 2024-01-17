from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Tag


async def create_tag(tag: Tag, db: AsyncSession):
    stmt = select(Tag).filter_by(name=tag.name)
    db_tag = await db.execute(stmt)
    db_tag = tag.scalar_one_or_none()
    if db_tag:
        return db_tag
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag
