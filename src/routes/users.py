from fastapi import (APIRouter, HTTPException, Depends, status, UploadFile, File, )
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
    The get_current_user function is used to get the current user from the database.

    :param file: UploadFile: Get the file from the request.
    :param user: User: Get the current user from the database.
    :param db: AsyncSession: Access the database.
    :return: The user object.
    """
    res_url, public_id = await CloudService.upload_picture(user.id, file)
    user = await repositories_users.update_avatar(user.full_name, res_url, db, public_id)
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user(user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It uses the auth_service to retrieve the current user,
        and returns it if found.
    
    :param user: User: Get the current user
    :param db: AsyncSession: Inject the database session
    :return: The user object
    """
    picture_count = await repositories_users.get_picture_count(db, user)
    
    return user


@router.get("/{username}", response_model=AnotherUsers)
async def get_user_profile(username: str, db: AsyncSession = Depends(get_db)):
    """
    Get the profile of a specific user by their username.

    :param username: str: Username of the user to retrieve.
    :param db: AsyncSession: Database session.
    :return: The user object.
    """
    user_info = await repositories_users.get_user_by_username(username, db)
    picture_count = await repositories_users.get_picture_count(db, user_info)
 
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
    Update the information of the currently logged-in user.

    :param user_update: UserUpdate: Data to update the user profile.
    :param user: User: Current logged-in user.
    :param db: AsyncSession: Database session.
    :return: The updated user object.
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
    Ban a user by their username. Only admins can perform this action.

    :param username: str: Username of the user to ban.
    :param current_user: User: Current logged-in user.
    :param db: AsyncSession: Database session.
    :return: Confirmation message.
    """
    if not current_user.role == Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action.",
        )

    await repositories_users.ban_user(username, db)
    return {"message": f"{username} has been banned."}
