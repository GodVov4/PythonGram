from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User
from src.schemas.users import UserSchema, UserUpdate


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function returns a user object from the database based on the email address provided.
        If no user is found, None is returned.
    
    :param email: str: Specify the type of the parameter
    :param db: AsyncSession: Pass the database session into the function
    :return: A single user object
    :doc-author: Trelent
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.
        It takes a UserSchema object as input and returns the newly created user.
    
    :param body: UserSchema: Validate the request body
    :param db: AsyncSession: Pass in the database session
    :return: A user object
    :doc-author: Trelent
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
    :doc-author: Trelent
    """
    user.refresh_token = token
    await db.commit()


async def update_avatar(email, url: str, db: AsyncSession) -> User:
    """
    The update_avatar function updates the avatar of a user.
    
    Args:
        email (str): The email address of the user to update.
        url (str): The URL for the new avatar image.
        db (AsyncSession): An async database session object, used to commit changes and query data from a database.  This is an example of dependency injection, which allows us to mock out this function in our tests without having access to an actual database connection.
    
    :param email: Find the user in the database
    :param url: str: Specify the type of the url parameter
    :param db: AsyncSession: Pass in the database session object
    :return: A user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def get_user_by_username(username: str,  db: AsyncSession):
    """
        Get a user by their username from the database.

        :param full_name: str: Username of the user to retrieve.
        :param db: AsyncSession: Database session.
        :return: User: The user object.
        """
    return await db.query(User).filter(User.full_name == username).first()


async def update_user(email: str, user_update: UserUpdate, db: AsyncSession):
    """
    Update user information in the database.

    :param email: str: Email of the user to update.
    :param user_update: UserUpdate: Data to update the user profile.
    :param db: AsyncSession: Database session.
    :return: User: The updated user object.
    """
    user = await db.query(User).filter(User.email == email).first()

    if user:
        for field, value in user_update.__dict__.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)
        return user
    else:
        return None
    

async def ban_user(username: str, db: AsyncSession):
    """
    Ban a user by updating their status in the database.

    :param username: str: Username of the user to ban.
    :param db: AsyncSession: Database session.
    """
    user = await db.query(User).filter(User.full_name == username).first()

    if user:
        user.ban = True
        await db.commit()
        return True 
    else:
        return False
    


