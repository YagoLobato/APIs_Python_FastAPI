from typing import Generator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from pydantic import BaseModel 

from core.database import async_session
from core.security import verificar_senha
from core.config import settings
from core.auth import oauth2_schema
from models.models_usuarios import UsuarioModel

async def get_session() -> Generator:
    session: AsyncSession = async_session()
    try:
        yield session
    finally:
        await session.close()
        
class TokenData(BaseModel):
    user_name: Optional[str] = None
    
async def get_usuario_logado(
    token: str = Depends(oauth2_schema), db: AsyncSession = Depends(get_session)
) -> UsuarioModel:
    credenciais_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_name: str = payload.get("sub")
        if user_name is None:
            raise credenciais_invalidas
        token_data = TokenData(user_name=user_name)
    except JWTError:
        raise credenciais_invalidas

    async with db as session:
        query = select(UsuarioModel).where(UsuarioModel.email == token_data.user_name)
        result = await session.execute(query)
        usuario: UsuarioModel = result.scalars().unique().one_or_none()
        if usuario is None:
            raise credenciais_invalidas
        return usuario