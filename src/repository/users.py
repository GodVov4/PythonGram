from fastapi import Depends
from libgravatar import Gravatar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Picture
from src.schemas.users import UserSchema, UserUpdate


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function returns a user object from the database based on the email address provided.
        If no user is found, None is returned.
    
    :param email: str: Specify the type of the parameter
    :param db: AsyncSession: Pass the database session into the function
    :return: A single user object
    """
    stmt = select(User).filter_by(email=email)
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

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


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


async def update_avatar(email, url: str, db: AsyncSession) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param email: Find the user in the database
    :param url: str: Specify the type of the url parameter
    :param db: AsyncSession: Pass in the database session object
    :return: A user object
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    return user


async def get_user_by_username(username: str, db: AsyncSession):
    """
    Get a user by their username from the database.

    :param username: str: Username of the user to retrieve.
    :param db: AsyncSession: Database session.
    :return: User: The user object.
    """
    stmt = select(User).filter_by(full_name=username)
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
    user = user.scalar_one_or_none()

    if user:
        for field, value in user_update.__dict__.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return user
    else:
        return None


async def get_picture_count(db: AsyncSession, user: User):
    stmt = select(Picture).filter_by(user=user)  # TODO: maybe user_id=user.id?
    pictures = await db.execute(stmt)
    picture_count = len(pictures.all())
 
    return picture_count


async def ban_user(username: str, db: AsyncSession):
    """
    Ban a user by updating their status in the database.

    :param username: str: Username of the user to ban.
    :param db: AsyncSession: Database session.
    """
    stmt = select(User).filter_by(full_name=username)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    if user:
        user.ban = True
        await db.commit()
        return True
    else:
        return False
