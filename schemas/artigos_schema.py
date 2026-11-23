from typing import Optional
from pydantic import BaseModel, ConfigDict

class ArtigoSchema(BaseModel):
    id: Optional[int] = None
    titulo: str
    url_fonte: str
    usuario_id: int
    descricao: str

    model_config = ConfigDict(from_attributes=True)