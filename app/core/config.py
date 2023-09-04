from pydantic import EmailStr, BaseSettings
import os


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SQLALCHEMY_DATABASE_URI: str
    SQLALCHEMY_DATABASE_URI_TEST: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PW: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 10080 minutes -> 7 days
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

    class Config:
        env_file = f'{os.path.dirname(os.path.abspath(__file__))}/../../.env'


settings = Settings(
    _env_file_encoding='utf-8'
)
