from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository import comments as repo_comm
from src.database.db import get_db
from src.schemas.comment import CommentSchema, CommentResponse

router = APIRouter(prefix='/comments', tags=['comments'])


@router.post('/', response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(body: CommentSchema, db: AsyncSession = Depends(get_db)):
    comment = await repo_comm.create_comment(body, db)
    return comment


@router.get('/', response_model=list[CommentResponse])
async def get_comments(skip: int, limit: int, db: AsyncSession = Depends(get_db)):
    comments = await repo_comm.get_comments(skip, limit, db)
    return comments


@router.get('/{comment_id}', response_model=CommentResponse)
async def get_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    comment = await repo_comm.get_comment(comment_id, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Comment not found')
    return comment


@router.put('/{comment_id}', response_model=CommentResponse)
async def update_comment(comment_id: int, body, db: AsyncSession = Depends(get_db)):
    comment = await repo_comm.update_comment(comment_id, body, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Comment not found')
    return comment


@router.delete('/{comment_id}', response_model=CommentResponse)
async def delete_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    comment = await repo_comm.delete_comment(comment_id, db)
    return comment
