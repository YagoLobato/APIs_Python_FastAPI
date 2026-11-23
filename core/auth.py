from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from models.usuario_model import UsuarioModel
from core.config import settings
from core.security import verificar_senha

oauth2_schema = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/usuarios/login")


async def autenticar_usuario(
    email: EmailStr, senha: str, db: AsyncSession
) -> Optional[UsuarioModel]:
    query = select(UsuarioModel).where(UsuarioModel.email == email)
    result = await db.execute(query)
    usuario = result.scalars().first()

    if not usuario or not verificar_senha(senha, usuario.senha):
        return None
    return usuario


def _criar_token(tipo_token: str, tempo_expiracao: timedelta, sub: str) -> str:
    agora = datetime.now(timezone.utc)
    payload = {
        "type": tipo_token,
        "exp": agora + tempo_expiracao,
        "iat": agora,
        "sub": str(sub),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)


def criar_token_acesso(sub: str) -> str:
    return _criar_token(
        tipo_token="access_token",
        tempo_expiracao=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        sub=sub,
    )