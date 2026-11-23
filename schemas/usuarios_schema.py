from typing import Optional, List
from pydantic import BaseModel, EmailStr

from schemas.artigos_schema import ArtigoSchema

class UsuarioSchemaBase(BaseModel):
    id: Optional[int] = None
    nome: str
    email: EmailStr
    senha: str
    ativo: bool = True
    eh_admin: bool = False

    class Config:
        orm_mode = True

class UsuarioSchemaCreate(UsuarioSchemaBase):
    senha: str
    
class UsuarioSchemaArtigos(UsuarioSchemaBase):
    artigos: Optional[List[ArtigoSchema]] = []
    
class UsuaruioSchemaUpdate(UsuarioSchemaBase):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    senha: Optional[str] = None
    ativo: Optional[bool] = None
    eh_admin: Optional[bool] = None