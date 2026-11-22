from typing import Optional
from pydantic import BaseModel, Field

class CursoSchema(BaseModel):
    id: Optional[int] = None
    nome: str = Field(..., max_length=100)
    aulas: int = Field(..., gt=0)
    horas: int = Field(..., gt=0)
    
    class Config:
        orm_mode = True