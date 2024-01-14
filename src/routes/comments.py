from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository import comments as repo_comm
from src.routes.users import get_current_user
from src.schemas.comment import CommentSchema, CommentResponse

router = APIRouter(prefix='/comments', tags=['comments'])


@router.post('/', response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
        body: CommentSchema,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    comment = await repo_comm.create_comment(body, db, user)
    return comment


@router.get('/', response_model=list[CommentResponse])
async def get_comments(
        picture_id: int,
        skip: int,
        limit: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    comments = await repo_comm.get_comments(picture_id, skip, limit, db)
    return comments


@router.get('/{comment_id}', response_model=CommentResponse)
async def get_comment(
        comment_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    comment = await repo_comm.get_comment(comment_id, db, user)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Comment not found')
    return comment


@router.put('/{comment_id}', response_model=CommentResponse)
async def update_comment(
        comment_id: int,
        body: CommentSchema,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    comment = await repo_comm.update_comment(comment_id, body, db, user)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Comment not found')
    return comment


@router.delete('/{comment_id}', response_model=CommentResponse)
async def delete_comment(
        comment_id: int,
        db: AsyncSession = Depends(get_db),
        user: User = Depends(get_current_user),
):
    comment = await repo_comm.delete_comment(comment_id, db, user)
    return comment
