from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository.transform import TransformRepository
from src.schemas.transform import TransformCreate, TransformResponse, TransformUpdate
from src.services.auth import auth_service

router = APIRouter(prefix='/transform', tags=['transform'])


@router.post('/create_transform/{original_picture_id}', response_model=TransformResponse, status_code=status.HTTP_201_CREATED)
async def create_transform(
        request: TransformCreate,
        original_picture_id: int = Path(ge=1),
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    transform_repo = TransformRepository(session)
    transformation_params = request.transformation_params
    user_id = await transform_repo.get_user_id_by_picture_id(original_picture_id)

    if user_id is None:
        raise HTTPException(status_code=404, detail="Зображення не знайдено")
    if user_id != current_user.id and current_user.role != Role.admin:
        raise HTTPException(status_code=403, detail="Недостатньо прав для створення трансформації")
    if not transformation_params:
        raise HTTPException(status_code=400, detail="Необхідно вказати хоча б один параметр трансформації")

    transformed_picture = await transform_repo.create_transformed_picture(
        user_id=user_id,
        original_picture_id=original_picture_id,
        transformation_params=transformation_params
    )
    if transformed_picture is None:
        raise HTTPException(
            status_code=status.HTTP_404, detail='Трансформація не виконана')
    return transformed_picture


@router.get("/user_transforms", response_model=List[TransformResponse], status_code=status.HTTP_200_OK)
async def list_user_transforms(
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    transform_repo = TransformRepository(session)
    user_transforms = await transform_repo.get_user_transforms(current_user.id)
    if user_transforms is None:
        raise HTTPException(status_code=404, detail="Зображення не знайдено")
    return user_transforms


@router.get("/{transform_id}", response_model=TransformResponse, status_code=status.HTTP_200_OK)
async def get_transform(
        transform_id: int = Path(ge=1),
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    transform_repo = TransformRepository(session)
    transformed_picture = await transform_repo.get_transformed_picture(transform_id)
    if transformed_picture is None:
        raise HTTPException(status_code=404, detail="Зображення не знайдено")
    if transformed_picture.user_id != current_user.id and current_user.role != Role.admin:
        raise HTTPException(status_code=403, detail="Недостатньо прав для перегляду цього зображення")
    return transformed_picture


@router.get("/{transform_id}/qr", status_code=status.HTTP_200_OK)
async def get_transform_qr(
        transform_id: int = Path(ge=1),
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    transform_repo = TransformRepository(session)

    transformed_picture = await transform_repo.get_transformed_picture(transform_id)
    if not transformed_picture:
        raise HTTPException(status_code=404, detail="QR-код не знайдено")
    if transformed_picture.user_id != current_user.id and current_user.role != Role.admin:
        raise HTTPException(status_code=403, detail="Недостатньо прав для перегляду цього зображення")

    return {"qr_url": transformed_picture.qr_url}


@router.patch("/{transform_id}", response_model=TransformResponse, status_code=status.HTTP_200_OK)
async def update_transform(
        request: TransformUpdate,
        transform_id: int = Path(ge=1),
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    transform_repo = TransformRepository(session)
    transformed_picture = await transform_repo.get_transformed_picture(transform_id)

    if not transformed_picture:
        raise HTTPException(status_code=404, detail="Зображення не знайдено")
    if transformed_picture.user_id != current_user.id and current_user.role != Role.admin:
        raise HTTPException(status_code=403, detail="Недостатньо прав для редагування цього зображення")

    new_transformed_picture = await transform_repo.update_transformed_picture(
        transformed_picture_id=transform_id,
        transformation_params=request.transformation_params)

    if not new_transformed_picture:
        raise HTTPException(status_code=404, detail= "Трансформація не виконана")
    return new_transformed_picture


@router.delete("/{transform_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transform(
        transform_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    transform_repo = TransformRepository(session)

    # Перевірка, чи користувач є власником трансформованого зображення
    transformed_picture = await transform_repo.get_transformed_picture(transform_id)
    if not transformed_picture:
        raise HTTPException(status_code=404, detail="Трансформоване зображення не знайдено")
    if transformed_picture.user_id != current_user.id and current_user.role != Role.admin:
        raise HTTPException(status_code=403, detail="Недостатньо прав для видалення цього зображення")

    success = await transform_repo.delete_transformed_picture(transform_id)
    if not success:
        raise HTTPException(status_code=404, detail="Видалення не виконано")
