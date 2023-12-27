from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f'{os.path.dirname(os.path.abspath(__file__))}/../../.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    API_V1_STR: str = "/api/v1"
    SQLALCHEMY_DATABASE_URI: str
    SQLALCHEMY_DATABASE_URI_TEST: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PW: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 10080 minutes -> 7 days
    RESET_PASSWORD_EXPIRE_MINUTES: int = 10
    MAIL_USE_TLS: bool = True
    MAIL_HOST: str | None = None
    MAIL_PORT: int | None = None
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    MAIL_TEMPLATES_DIR: str = None
    MAIL_FROM: str = "BABA NURA"
    PROJECT_NAME: str = "CHEBUREKI.RU"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8002
    ELASTICSEARCH_URL: str
    STATIC_DIR: str
    BROKER: str
    BACKEND: str


settings = Settings()
