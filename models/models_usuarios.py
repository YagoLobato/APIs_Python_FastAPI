from core.config import settings
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship 

class UsuarioModel(settings.DBBaseModel):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha = Column(String)
    ativo = Column(Boolean, default=True)
    eh_admin = Column(Boolean, default=False)
    artigos = relationship("ArtigoModel", back_populates="autor", lazy="joined", cascade="all, delete-orphan", uselist=False)