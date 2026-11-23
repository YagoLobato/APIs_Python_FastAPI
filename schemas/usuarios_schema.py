from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr

from schemas.artigos_schema import ArtigoSchema


class UsuarioSchemaBase(BaseModel):
    id: Optional[int] = None
    nome: str
    email: EmailStr
    ativo: bool = True
    eh_admin: bool = False

    model_config = ConfigDict(from_attributes=True)


class UsuarioSchemaCreate(UsuarioSchemaBase):
    senha: str


class UsuarioSchemaArtigos(UsuarioSchemaBase):
    artigos: List[ArtigoSchema] = []


class UsuarioSchemaUpdate(UsuarioSchemaBase):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    senha: Optional[str] = None
    ativo: Optional[bool] = None
    eh_admin: Optional[bool] = None