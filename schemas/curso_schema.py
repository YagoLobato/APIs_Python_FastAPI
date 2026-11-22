from typing import Optional
from pydantic import BaseModel

class CursoSchema(BaseModel):
    id: Optional[int] = None
    titulo: str
    aulas: int
    horas: int

    class Config:
        from_attributes = True