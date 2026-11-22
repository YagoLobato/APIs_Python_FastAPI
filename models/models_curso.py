from core.config import settings
from sqlachemy import Column, Integer, String  

class CursoModel(settings.SQLALCHEMY_DATABASE_URI):
    __tablename__ = "cursos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    aulas = Column(Integer, index=True)
    horas = Column(Integer, index=True)
  