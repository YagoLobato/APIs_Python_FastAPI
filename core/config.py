from typing import List
from pydantic import BaseSettings, Field, AnyHttpUrl
from sqlalchemy.ext.declarative import declarative_base

class Settings(BaseSettings):
    PROJECT_NAME: str = Field("fastapi_sqlalchemy", env="PROJECT_NAME")
    API_V1_STR: str = Field("/api/v1", env="API_V1_STR")
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=["http://localhost", "http://localhost:8080"],
        env="BACKEND_CORS_ORIGINS",
    )
    SQLALCHEMY_DATABASE_URI: str = Field("postgresql+asyncpg://postgres:Brato1474!@localhost:5432/faculdade_fastapi", env="SQLALCHEMY_DATABASE_URI")

    class Config:
        case_sensitive = True
        
settings = Settings()