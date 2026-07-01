from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date


class ReabastecimientoCreate(BaseModel):
    id_producto: int
    id_prediccion: Optional[int] = None
    cantidad_sugerida: int = Field(0, ge=0)


class ReabastecimientoUpdate(BaseModel):
    estado: Optional[Literal["PENDIENTE", "APROBADO", "COMPRADO", "CANCELADO"]] = None
    cantidad_sugerida: Optional[int] = Field(None, ge=0)


class ReabastecimientoResponse(BaseModel):
    id_reabastecimiento: int
    id_producto: int
    id_prediccion: Optional[int]
    fecha_generacion: Optional[date]
    cantidad_sugerida: int
    estado: str

    class Config:
        from_attributes = True
