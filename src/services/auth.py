from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt  # noqa
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.database.db import get_db
from src.entity.models import Blacklisted
from src.repository import users as repository_users


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM

    def verify_password(self, plain_password: str, hashed_password: str):  # +TODO Add type hints
        """
        The verify_password function takes a plain-text password and the hashed version of that password,
        and returns True if they match, False otherwise. This is used to verify that the user's login attempt
        is valid.
        
        :param self: Represent the instance of the class
        :param plain_password: str: Pass the plain text password to be hashed
        :param hashed_password: str: Pass in the hashed password from the database
        :return: A boolean
        """
        return self.pwd_context.verify(plain_password, hashed_password)

   
    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password as input and returns the hash of that password.
            The function uses the pwd_context object to generate a hash from the given password.
        
        :param self: Represent the instance of the class
        :param password: str: Get the password from the user
        :return: A hash of the password
        """
        return self.pwd_context.hash(password)

    
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_access_token function creates a new access token for the user.

        :param self: Represent the instance of the class
        :param data: dict: Pass the data to be encoded in the jwt token
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: An encoded access token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=1500000)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_refresh_token function creates a refresh token for the user.

        :param self: Represent the instance of the class
        :param data: dict: Pass the user data to be encoded in the token
        :param expires_delta: Optional[float]: Set the expiration time for the refresh token
        :return: An encoded refresh token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    
    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function is used to decode the refresh token.

        The function will raise an HTTPException if the token is invalid or has expired.
        If the token is valid, it will return a string with the email address of
        user who owns that refresh_token.
        
        :param self: Represent the instance of a class
        :param refresh_token: str: Pass the refresh token to the function
        :return: The email of the user
        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    
    async def add_token_to_blacklist(self, user_id: int, token: str, db: AsyncSession = Depends(get_db)):
        """
        The add_token_to_blacklist function adds a token to the blacklist.

        :param self: Represent the instance of a class
        :param user_id: int: Identify the user that is associated with the token
        :param token: str: Pass in the token that is to be blacklisted
        :param db: AsyncSession: Pass in the database session
        :return: None
        """

        async with db as session:
            existing_token = await session.query(Blacklisted).filter_by(token=token).first()
            if existing_token:
                return
            new_blacklisted_token = Blacklisted(user_id=user_id, token=token)
            session.add(new_blacklisted_token)
            session.commit()

   
    async def is_token_blacklisted(self, token: str, db: AsyncSession = Depends(get_db)):
        """
        The is_token_blacklisted function checks if a token is blacklisted.
        
        :param self: Represent the instance of a class
        :param token: str: Pass the token to be checked
        :param db: AsyncSession: Get the database session
        :return: A boolean value
        """
        async with db as session:
            stmt = select(Blacklisted).filter_by(token=token)
            blacklisted_token = await session.execute(stmt)
            blacklisted_token = blacklisted_token.scalar_one_or_none()
            return bool(blacklisted_token)

    
    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        """
        The get_current_user function is a dependency that will be used in the UserRouter class.
        It takes an access token as input and returns the user object associated with it.
        
        :param self: Represent the instance of a class
        :param token: str: Pass the token to the function
        :param db: Session: Get the database session from the dependency
        :return: The user object
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        if await self.is_token_blacklisted(token, db):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is blacklisted. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        if user.ban:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your account has been banned.")
        return user
    
  



auth_service = Auth()
