from typing import List, ClassVar
from pydantic import Field, AnyHttpUrl
from pydantic_settings import BaseSettings
from sqlalchemy.orm import declarative_base


class Settings(BaseSettings):
    PROJECT_NAME: str = Field("fastapi_sqlalchemy", env="PROJECT_NAME")
    API_V1_STR: str = Field("/api/v1", env="API_V1_STR")
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=["http://localhost", "http://localhost:8080"],
        env="BACKEND_CORS_ORIGINS",
    )
    SQLALCHEMY_DATABASE_URI: str = Field(..., env="SQLALCHEMY_DATABASE_URI")
    DBBaseModel: ClassVar = declarative_base()

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()