from pydantic import BaseModel
from typing import Optional
from datetime import date


class PrediccionCreate(BaseModel):
    id_modelo: int
    id_producto: int
    periodo: Optional[str] = None
    demanda_estimada: int = 0


class PrediccionResponse(BaseModel):
    id_prediccion: int
    id_modelo: int
    id_producto: int
    fecha_prediccion: Optional[date]
    periodo: Optional[str]
    demanda_estimada: int

    class Config:
        from_attributes = True
