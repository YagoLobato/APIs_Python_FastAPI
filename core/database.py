from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine 

from core.config import settings

engine: AsyncEngine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=True)
async_session = sessionmaker(engine, autocommit=False, autoflush=False, expire_on_commit=False, class_=AsyncSession)
