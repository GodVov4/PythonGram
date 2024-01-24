from fastapi import APIRouter, HTTPException, Depends, status, Query, Path
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository import comments as repo_comm
from src.schemas.comment import CommentSchema, CommentResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix='/comments', tags=['comments'])
delete_access = RoleAccess([Role.admin, Role.moderator])


@router.post('/{picture_id}', response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
        body: CommentSchema,
        picture_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    if not body.text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Text is required')
    try:
        comment = await repo_comm.create_comment(body, picture_id, db, user)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='BAD REQUEST')
    return comment


@router.get('/all/{picture_id}', response_model=list[CommentResponse])
async def get_comments(
        picture_id: int = Path(ge=1),
        offset: int = Query(0, ge=0),
        limit: int = Query(10, ge=10, le=100),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    comments = await repo_comm.get_comments(picture_id, offset, limit, db)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")
    return comments


@router.get('/{comment_id}', response_model=CommentResponse)
async def get_comment(
        comment_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    comment = await repo_comm.get_comment(comment_id, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Comment not found')
    return comment


@router.patch('/{comment_id}', response_model=CommentResponse)
async def update_comment(
        body: CommentSchema,
        comment_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    if not body.text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Text is required')
    try:
        comment = await repo_comm.update_comment(comment_id, body, db, user)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='BAD REQUEST')
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Comment not found')
    return comment


@router.delete('/{comment_id}', response_model=CommentResponse, dependencies=[Depends(delete_access)])
async def delete_comment(
        comment_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
):
    comment = await repo_comm.delete_comment(comment_id, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment
