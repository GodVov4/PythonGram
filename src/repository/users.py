from fastapi import Depends
from libgravatar import Gravatar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Picture, Role
from src.schemas.users import UserSchema, UserUpdate
from src.services.auth import auth_service


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function returns a user object from the database based on the email address provided.
        If no user is found, None is returned.
    
    :param email: str: Specify the type of the parameter
    :param db: AsyncSession: Pass the database session into the function
    :return: A single user object
    """
    stmt = select(User).where(User.email == email)
    user = await db.execute(stmt)
    user = user.unique().scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.
        It takes a UserSchema object as input and returns the newly created user.
    
    :param body: UserSchema: Validate the request body
    :param db: AsyncSession: Pass in the database session
    :return: A user object
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    is_first_user = await check_is_first_user(db)
    if is_first_user:
        new_user = User(**body.model_dump(),
                        avatar=avatar, role=Role.admin)
    else:
        new_user = User(**body.model_dump(), avatar=avatar)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def check_is_first_user(db: AsyncSession):
    """
    Check if there are any users in the database.
    
    :param db: AsyncSession: Pass in the database session
    :return: True if there are no users in the database, False otherwise
    """
    stmt = select(User).limit(1)
    result = await db.execute(stmt)
    return result.unique().scalar_one_or_none() is None


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    The update_token function updates the refresh token for a user.
    
    :param user: User: Identify the user that is being updated
    :param token: str | None: Specify that the token parameter can either be a string or none
    :param db: AsyncSession: Pass the database session to the function
    :return: Nothing
    """
    user.refresh_token = token
    await db.commit()


async def update_avatar(full_name, url: str, db: AsyncSession, public_id) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param full_name: Specify the type of the full_name parameter
    :param url: str: Specify the type of the url parameter
    :param db: AsyncSession: Pass in the database session object
    :param public_id: str: Specify the type of the public_id parameter
    :return: A user object
    """
    user = await get_user_by_username(full_name, db)
    user.avatar = url
    picture = Picture(url=url, cloudinary_public_id=public_id, description=None, user_id=user.id)
    db.add(picture)
    db.add(user)
    await db.commit()
    await db.refresh(picture)
    await db.refresh(user)
    return user


async def get_user_by_username(full_name: str, db: AsyncSession = Depends(get_db)):
    """
    Get a user by their username from the database.

    :param full_name: str: Username of the user to retrieve.
    :param db: AsyncSession: Database session.
    :return: User: The user object.
    """
    stmt = select(User).filter_by(full_name=full_name)
    user = await db.execute(stmt)
    user = user.unique().scalar_one_or_none()
    return user


async def update_user(email: str, user_update: UserUpdate, db: AsyncSession):
    """
    Update user information in the database.

    :param email: str: Email of the user to update.
    :param user_update: UserUpdate: Data to update the user profile.
    :param db: AsyncSession: Database session.
    :return: User: The updated user object.
    """

    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.unique().scalar_one_or_none()

    if user:
        for field, value in user_update.__dict__.items():
            if field == 'password':
                setattr(user, field, auth_service.get_password_hash(value))
            else:
                setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return user
    else:
        return None


async def get_picture_count(db: AsyncSession, user: User):
    """
    The get_picture_count function is used to get the number of pictures a user has uploaded.
    It takes in an AsyncSession object and a User object as parameters.
    It returns the number of pictures that user has uploaded.
    
    :param db: AsyncSession: Connect to the database
    :param user: User: Get the user object from the database
    :return: The picture count of the user
    """
    stmt = select(Picture).filter_by(user=user)
    pictures = await db.execute(stmt)

    if pictures is None:
        picture_count = 1
    else:
        picture_count = len(pictures.unique().all())
    user.picture_count = picture_count
    await db.commit()
    await db.refresh(user)



async def ban_user(username: str, db: AsyncSession):
    """
    Ban a user by updating their status in the database.

    :param username: str: Username of the user to ban.
    :param db: AsyncSession: Database session.
    """
    stmt = select(User).filter_by(full_name=username)
    user = await db.execute(stmt)
    user = user.unique().scalar_one_or_none()
    if user:
        user.ban = True
        await db.commit()
        return True
    else:
        return False
