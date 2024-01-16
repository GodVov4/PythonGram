from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository.transform import TransformRepository
from src.schemas.transform import TransformCreate, TransformResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/transform', tags=['transform'])


@router.post("/create_transform", response_model=TransformResponse,
             status_code=status.HTTP_201_CREATED, tags=["transform"])
async def create_transform(request: TransformCreate,
                           current_user: User = Depends(auth_service.get_current_user),
                           session: AsyncSession = Depends(get_db)):
    if request.resize_params is None and request.compression_quality is None and \
            request.filter_params is None and request.rotation_angle is None and \
            request.mirror is None:
        raise HTTPException(status_code=400, detail="Необхідно вказати хоча б один параметр трансформації")

    transform_repo = TransformRepository(session)

    original_picture_id = request.original_picture_id
    # transformation_params = request.transformation_params
    user_id = await transform_repo.get_user_id_by_picture_id(original_picture_id)

    if user_id is None or user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостатньо прав для створення трансформації")

    try:
        transformed_picture = await transform_repo.create_transformed_picture(
            user_id=user_id,
            original_picture_id=original_picture_id,
            transformation_params=[
                request.resize_params,
                request.compression_quality,
                request.filter_params,
                request.rotation_angle,
                request.mirror
            ])

        return transformed_picture
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{trans_id}", response_model=TransformResponse,
            status_code=status.HTTP_200_OK, tags=["transform"])
async def get_transform(trans_id: int,
                        current_user: User = Depends(auth_service.get_current_user),
                        session: AsyncSession = Depends(get_db)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Необхідна авторизація")
    transform_repo = TransformRepository(session)
    transformed_picture = await transform_repo.get_transformed_picture(trans_id)
    if transformed_picture is None:
        raise HTTPException(status_code=404, detail="Зображення не знайдено")
    return transformed_picture


@router.delete("/{trans_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["transform"])
async def delete_transform(
        trans_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db)):
    transform_repo = TransformRepository(session)

    # Перевірка, чи користувач є власником трансформованого зображення
    transformed_picture = await transform_repo.get_transformed_picture(trans_id)
    if not transformed_picture or transformed_picture.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостатньо прав для видалення цього зображення")

    success = await transform_repo.delete_transformed_picture(trans_id)
    if not success:
        raise HTTPException(status_code=404, detail="Трансформоване зображення не знайдено або вже видалено")
