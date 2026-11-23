from typing import List, ClassVar
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.orm import declarative_base


class Settings(BaseSettings):
    PROJECT_NAME: str = "fastapi_sqlalchemy"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:8080",
    ]
    SQLALCHEMY_DATABASE_URI: str
    DBBaseModel: ClassVar = declarative_base()

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    JWT_SECRET_KEY: str 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 60 minutes


settings = Settings()