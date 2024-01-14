from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str
    SECRET_KEY_JWT: str
    ALGORITHM: str
    # MAIL_USERNAME: EmailStr
    # MAIL_PASSWORD: str
    # MAIL_FROM: str
    # MAIL_PORT: int
    # MAIL_SERVER: str
    REDIS_DOMAIN: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    CLD_NAME: str
    CLD_API_KEY: str
    CLD_API_SECRET: str

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")  # noqa


config = Settings()
