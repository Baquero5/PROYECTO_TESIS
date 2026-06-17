from pydantic import BaseModel
from typing import Optional
from datetime import date


class ReabastecimientoCreate(BaseModel):
    id_producto: int
    id_prediccion: Optional[int] = None
    cantidad_sugerida: int = 0


class ReabastecimientoUpdate(BaseModel):
    estado: Optional[str] = None
    cantidad_sugerida: Optional[int] = None


class ReabastecimientoResponse(BaseModel):
    id_reabastecimiento: int
    id_producto: int
    id_prediccion: Optional[int]
    fecha_generacion: Optional[date]
    cantidad_sugerida: int
    estado: str

    class Config:
        from_attributes = True
