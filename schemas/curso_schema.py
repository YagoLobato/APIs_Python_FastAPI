from typing import Optional
from pydantic import BaseModel, ConfigDict


class CursoSchema(BaseModel):
    id: Optional[int] = None
    titulo: str
    aulas: int
    horas: int

    model_config = ConfigDict(from_attributes=True)