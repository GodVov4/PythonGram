from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository import users as repositories_users
from src.schemas.users import UserResponse, UserUpdate, AnotherUsers
from src.services.auth import auth_service
from src.services.cloudstore import CloudService

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/avatar", response_model=UserResponse)
async def get_user_avatar(
        file: UploadFile = File(),
        user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to upload and update the user's avatar.

    :param file: The avatar image file to be uploaded.
    :type file: UploadFile
    :param user: Current authenticated user (dependency injection).
    :type user: User
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: The updated user information.
    :rtype: UserResponse
    """
    res_url, public_id = await CloudService.upload_picture(user.id, file, f'PythonGram/user_{user.id}/avatar')
    user = await repositories_users.update_avatar(user.full_name, res_url, db, public_id)
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user(user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Endpoint to retrieve the information of the currently authenticated user.

    :param user: Current authenticated user (dependency injection).
    :type user: User
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: The information of the currently authenticated user.
    :rtype: UserResponse
    """
    await repositories_users.get_picture_count(db, user)
    return user


@router.get("/{username}", response_model=AnotherUsers)
async def get_user_profile(username: str, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to retrieve the profile information of a specific user by username.

    :param username: Username of the user to be retrieved.
    :type username: str
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: The profile information of the specified user.
    :rtype: AnotherUsers
    :raises HTTPException: If the user is not found.
    """
    user_info = await repositories_users.get_user_by_username(username, db)
    await repositories_users.get_picture_count(db, user_info)

    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return user_info


@router.patch("/me", response_model=UserResponse)
async def update_own_profile(
        user_update: UserUpdate,
        user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to update the profile of the currently authenticated user.

    :param user_update: UserUpdate instance containing the updated user information.
    :type user_update: UserUpdate
    :param user: Current authenticated user (dependency injection).
    :type user: User
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :return: The updated user information.
    :rtype: UserResponse
    """
    updated_user = await repositories_users.update_user(user.email, user_update, db)

    return updated_user


@router.patch("/admin/{username}/ban")
async def ban_user(
        username: str,
        current_user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to ban a user by the admin.

    :param username: Username of the user to be banned.
    :type username: str
    :param current_user: Current authenticated user (dependency injection).
    :type current_user: User
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :raises HTTPException: If the current user is not an admin or if the user to be banned is not found.
    :return: A message indicating the success of the operation.
    :rtype: dict
    """
    if not current_user.role == Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action.",
        )

    await repositories_users.ban_user(username, db)
    return {"message": f"{username} has been banned."}
