from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository.transform import TransformRepository
from src.schemas.transform import TransformCreate, TransformResponse, TransformUpdate
from src.services.auth import auth_service

router = APIRouter(prefix='/transform', tags=['transform'])


def access_checking(picture, current_user: User):
    """
    The access_checking method checks if the current user can access the specified picture.

    :param picture: The picture object.
    :param current_user: The current user.
    :return: None
    """
    if not picture:
        raise HTTPException(status_code=404, detail="Зображення не знайдено")
    if picture.user_id != current_user.id and current_user.role != Role.admin:
        raise HTTPException(status_code=403, detail="Недостатньо прав для цієї операції")
    return


@router.post('/create_transform/{original_picture_id}', response_model=TransformResponse, status_code=status.HTTP_201_CREATED)
async def create_transform(
        request: TransformCreate,
        original_picture_id: int = Path(ge=1),
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    """
    The create_transform method creates a new transformed picture.

    :param request: The request object containing the transformation parameters.
    :param original_picture_id: The ID of the original picture.
    :param current_user: The current user.
    :param session: The database session.
    :return: The transformed picture.

    Available transformation params:
    - `width`: The width of the transformed image. 100-2000.
    - `height`: The height of the transformed image. 100-2000.
    - `crop`: The crop mode. `fill`, `limit`, `scale`, `thumb`, `fit`, `lfill`
    - `effect`: `grayscale`, `sepia`, `vignette`, `cartoonify`,`pixelate`, `blur`, `brightness`,
    `contrast`, `saturation`, `sharpen`
    - `border`: `5px_solid_lightblue`, `5px_dotted_lightblue`, `5px_dashed_lightblue`
    - `angle`: 0-360
    """
    transform_repo = TransformRepository(session)
    transformation_params = request.transformation_params
    picture = await transform_repo.get_picture_by_id(original_picture_id)
    access_checking(picture, current_user)
    if not transformation_params:
        raise HTTPException(status_code=400, detail="Необхідно вказати хоча б один параметр трансформації")
    transformed_picture = await transform_repo.create_transformed_picture(
        user_id=picture.user_id,
        original_picture_id=original_picture_id,
        transformation_params=transformation_params
    )
    if transformed_picture is None:
        raise HTTPException(
            status_code=500, detail='Трансформація не виконана')
    return transformed_picture


@router.get("/user_transforms", response_model=List[TransformResponse], status_code=status.HTTP_200_OK)
async def list_user_transforms(
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    """
    The list_user_transforms method returns a list of transformed pictures created by the current user.

    :param current_user: The current user.
    :param session: The database session.
    :return: A list of transformed pictures.
    """
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
    """
    The get_transform method returns the transformed picture with the specified ID.

    :param transform_id: The ID of the transformed picture.
    :param current_user: The current user.
    :param session: The database session.
    :return: The transformed picture.
    """
    transform_repo = TransformRepository(session)
    transformed_picture = await transform_repo.get_transformed_picture(transform_id)
    access_checking(transformed_picture, current_user)
    return transformed_picture


@router.get("/{transform_id}/qr", status_code=status.HTTP_200_OK)
async def get_transform_qr(
        transform_id: int = Path(ge=1),
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    """
    The get_transform_qr method returns the QR code of the transformed picture with the specified ID.

    :param transform_id: The ID of the transformed picture.
    :param current_user: The current user.
    :param session: The database session.
    :return: The QR code of the transformed picture.
    """
    transform_repo = TransformRepository(session)
    transformed_picture = await transform_repo.get_transformed_picture(transform_id)
    access_checking(transformed_picture, current_user)
    return {"qr_url": transformed_picture.qr_url}


@router.patch("/{transform_id}", response_model=TransformResponse, status_code=status.HTTP_200_OK)
async def update_transform(
        request: TransformUpdate,
        transform_id: int = Path(ge=1),
        current_user: User = Depends(auth_service.get_current_user),
        session: AsyncSession = Depends(get_db),
):
    """
    The update_transform method updates the transformation parameters of the transformed picture with the specified ID.

    :param request: The request object containing the transformation parameters.
    :param transform_id: The ID of the transformed picture.
    :param current_user: The current user.
    :param session: The database session.
    :return: The updated transformed picture.

    Available transformation params:
    - `width`: The width of the transformed image. 100-2000.
    - `height`: The height of the transformed image. 100-2000.
    - `crop`: The crop mode. `fill`, `limit`, `scale`, `thumb`, `fit`, `lfill`
    - `effect`: `grayscale`, `sepia`, `vignette`, `cartoonify`,`pixelate`, `blur`, `brightness`,
    `contrast`, `saturation`, `sharpen`
    - `border`: `5px_solid_lightblue`, `5px_dotted_lightblue`, `5px_dashed_lightblue`
    - `angle`: 0-360
    """
    transform_repo = TransformRepository(session)
    transformed_picture = await transform_repo.get_transformed_picture(transform_id)
    access_checking(transformed_picture, current_user)
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
    """
    The delete_transform method deletes the transformed picture with the specified ID.

    :param transform_id: The ID of the transformed picture to be deleted.
    :param current_user: The current user.
    :param session: The database session.
    """
    transform_repo = TransformRepository(session)
    transformed_picture = await transform_repo.get_transformed_picture(transform_id)
    access_checking(transformed_picture, current_user)
    success = await transform_repo.delete_transformed_picture(transform_id)
    if not success:
        raise HTTPException(status_code=404, detail="Видалення не виконано")
