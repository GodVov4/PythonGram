import pickle

import cloudinary
import cloudinary.uploader
from fastapi import (APIRouter, HTTPException,Depends,status,UploadFile,File,)

from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.schemas.users import UserResponse, UserUpdate, AnotherUsers
from src.services.auth import auth_service
from src.repository import users as repositories_users
from src.services.cloudstore import CloudService

router = APIRouter(prefix="/users", tags=["users"])



@router.patch("/avatar", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_current_user(
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
    :doc-author: Trelent
    """  
    res_url, public_id = CloudService.upload_picture(user.id, file.file)
    user = await repositories_users.update_avatar(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user

@router.get("/me", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))],)
async def get_current_user(user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It uses the auth_service to retrieve the current user,
        and returns it if found.
    
    :param user: User: Get the current user
    :return: The user object
    :doc-author: Trelent
    """
    picture_count = await repositories_users.get_picture_count(db, user)
    
    # Build the UserResponse object
    user_response = UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        avatar=user.avatar,
        role=user.role,
        picture_count=picture_count,
        created_at=user.created_at
    )

    return user_response


@router.get("/{username}", response_model=AnotherUsers, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_user_profile(username: str, current_user: User = Depends(auth_service.get_current_user)):
    """
    Get the profile of a specific user by their username.

    :param username: str: Username of the user to retrieve.
    :param current_user: User: Current logged-in user.
    :return: The user object.
    :doc-author: Trelent
    """
    user_info = await repositories_users.get_user_by_username(username)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    return user_info


@router.patch("/me", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def update_own_profile(
    user_update: UserUpdate,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the information of the currently logged-in user.

    :param user_update: UserUpdate: Data to update the user profile.
    :param current_user: User: Current logged-in user.
    :param db: AsyncSession: Database session.
    :return: The updated user object.
    :doc-author: Trelent
    """
    updated_user = await repositories_users.update_user(current_user.email, user_update, db)
    auth_service.cache.set(current_user.email, pickle.dumps(updated_user))
    auth_service.cache.expire(current_user.email, 300)

    return updated_user


@router.put("/admin/{username}/ban", dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def ban_user(username: str, current_user: User = Depends(auth_service.get_current_user)):
    """
    Ban a user by their username. Only admins can perform this action.

    :param username: str: Username of the user to ban.
    :param current_user: User: Current logged-in user.
    :return: Confirmation message.
    :doc-author: Trelent
    """
    if not current_user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have permission to perform this action.")

    await repositories_users.ban_user(username)
    return {"message": f"{username} has been banned."}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Log out the current user by blacklisting their access token.

    :param current_user: User: Current logged-in user.
    :param auth_service: AuthService: Authentication service instance.
    :return: Confirmation message.
    :doc-author: Trelent
    """
    await auth_service.add_token_to_blacklist(current_user.refresh_token)

    return {"message": "Logout successful."}
