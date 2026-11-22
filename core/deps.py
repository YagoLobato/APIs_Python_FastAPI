from typing import Generator
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import async_session

async def get_session() -> Generator:
    session: AsyncSession = async_session()
    try:
        yield session
    finally:
        await session.close()