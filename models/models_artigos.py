from core.config import settings
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class ArtigoModel(settings.DBBaseModel):
    __tablename__ = "artigos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String, index=True)
    url_fonte = Column(String)
    descricao = Column(String)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    autor = relationship("UsuarioModel", back_populates="artigos", lazy="selectin")