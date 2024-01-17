from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = 'postgresql://user:password@localhost:5432/db'
    SECRET_KEY_JWT: str = 'secret'
    ALGORITHM: str = 'HS256'
    # MAIL_USERNAME: EmailStr = 'example@mail.com'
    # MAIL_PASSWORD: str = 'password'
    # MAIL_FROM: str = 'example@mail.com'
    # MAIL_PORT: int = 587
    # MAIL_SERVER: str = 'smtp.gmail.com'
    REDIS_DOMAIN: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = 'password'
    CLD_NAME: str = 'cloud_name'
    CLD_API_KEY: str = 'api_key'
    CLD_API_SECRET: str = 'api_secret'

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")  # noqa


config = Settings()
