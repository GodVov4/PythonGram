from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository.transform import TransformRepository
from src.schemas.transform import TransformCreate, TransformResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/transform', tags=['transform'])


@router.post("/create_transform", response_model=TransformResponse, status_code=status.HTTP_201_CREATED,
             tags=["transform"],
             )
async def create_transform(
        request: TransformCreate,
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    transform_repo = TransformRepository(session)

    original_picture_id = request.original_picture_id

    if original_picture_id is None:
        raise HTTPException(status_code=400, detail="Необхідно вказати ID оригінального зображення")
    user_id = await transform_repo.get_user_id_by_picture_id(original_picture_id)
    if user_id is None or user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостатньо прав для створення трансформації")

    transformation_params = [
        param for param in [
            request.resize_params,
            request.compression_quality,
            request.filter_params,
            request.rotation_angle,
            request.mirror
        ] if param is not None
    ]

    if not transformation_params:
        raise HTTPException(status_code=400, detail="Необхідно вказати хоча б один параметр трансформації")

        # TODO: think about "return" (None), or "return get_picture_by_id(request.original_picture_id)"

    try:
        transformed_picture = await transform_repo.create_transformed_picture(
            user_id=user_id,
            original_picture_id=original_picture_id,
            transformation_params=transformation_params
        )

        return transformed_picture
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{transform_id}", response_model=TransformResponse, status_code=status.HTTP_200_OK, tags=["transform"],
            )
async def get_transform(
        transform_id: int = Path(ge=1),
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    transform_repo = TransformRepository(session)
    transformed_picture = await transform_repo.get_transformed_picture(transform_id)
    if transformed_picture is None:
        raise HTTPException(status_code=404, detail="Зображення не знайдено")
    return transformed_picture


@router.get("/{transform_id}/qr", status_code=status.HTTP_200_OK, tags=["transform"])
async def get_transform_qr(
        transform_id: int = Path(ge=1),
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    transform_repo = TransformRepository(session)

    transformed_picture = await transform_repo.get_transformed_picture(transform_id)
    if not transformed_picture:
        raise HTTPException(status_code=404, detail="QR-код не знайдено")

    # Повернення посилання на QR-код
    return {"qr_url": transformed_picture.qr_url}


@router.get("/user_transforms", response_model=List[TransformResponse], tags=["transform"])
async def list_user_transforms(
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    transform_repo = TransformRepository(session)
    user_transforms = await transform_repo.get_user_transforms(current_user.id)
    return user_transforms


@router.get("/user_transforms_qr", tags=["transform"])
async def list_user_transforms_qr(
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    transform_repo = TransformRepository(session)
    user_transforms = await transform_repo.get_user_transforms(current_user.id)

    qr_urls = [{"transform_id": transform.id, "qr_url": transform.qr_url}
               for transform in user_transforms if transform.qr_url]
    return qr_urls


@router.delete("/{transform_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["transform"])
async def delete_transform(
        transform_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    transform_repo = TransformRepository(session)

    # Перевірка, чи користувач є власником трансформованого зображення
    transformed_picture = await transform_repo.get_transformed_picture(transform_id)
    if not transformed_picture or transformed_picture.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Недостатньо прав для видалення цього зображення")

    success = await transform_repo.delete_transformed_picture(transform_id)
    if not success:
        raise HTTPException(status_code=404, detail="Трансформоване зображення не знайдено або вже видалено")
