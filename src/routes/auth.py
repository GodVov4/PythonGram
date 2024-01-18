from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository import users as repositories_users
from src.schemas.users import UserSchema, TokenSchema, UserResponse
from src.services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    The signup function creates a new user in the database.
        It takes a UserSchema object as input, and returns the newly created user.
    
    
    :param body: UserSchema: Validate the request body
    :param db: AsyncSession: Get the database session
    :return: A user object
    """
    # exist_user = await repositories_users.get_user_by_email(body.email, db)
    exist_user = await repositories_users.get_user_by_username(body.full_name, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)

    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    The login function is used to authenticate a user.
    It takes in the username and password of the user, and returns an access token if successful.
    
    
    :param body: OAuth2PasswordRequestForm: Validate the body of the request
    :param db: AsyncSession: Get a database session
    :return: A dict with three keys:
    """
    # user = await repositories_users.get_user_by_email(body.username, db)
    user = await repositories_users.get_user_by_username(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    if user.ban:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You were banned by an administrator")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", }


@router.get("/refresh_token", response_model=TokenSchema)
async def refresh_token(
        credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
        db: AsyncSession = Depends(get_db),
):
    """
    The refresh_token function is used to refresh the access token.
        The function takes in a refresh token and returns an access_token, 
        a new refresh_token, and the type of token (bearer).
    
    :param credentials: HTTPAuthorizationCredentials: Get the refresh token from the request header
    :param db: AsyncSession: Get the database session
    :param : Get the credentials from the request header
    :return: A dict with the access_token, refresh_token and token_type
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", }


@router.post("/logout")
async def logout(user: User = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Log out the current user by blacklisting their access token.

    :param user: User: Current logged-in user.
    :param db: AsyncSession: Database session.
    :return: Confirmation message.
    """
    await auth_service.add_token_to_blacklist(user.id, user.refresh_token, db)

    return {"message": "Logout successful."}
