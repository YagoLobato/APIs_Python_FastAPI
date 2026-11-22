from core.config import settings
from sqlalchemy import Column, Integer, String  

class CursoModel(settings.DBBaseModel):
    __tablename__ = "cursos"
    
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    aulas = Column(Integer, index=True)
    horas = Column(Integer, index=True)
  